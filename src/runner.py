import json
import logging
import os
import shlex
import threading
import time

import sh
from prometheus_client import Counter

import config
from pod_mgr import PodsNotAvailable


log = logging.getLogger("blackbox.runner")


DURATION_COUNTER = Counter(
    "black_box_test_duration_total", "Total duration of all test runs", ["plugin"]
)
RUN_COUNTER = Counter("black_box_test_runs_total", "Total count of test runs", ["plugin"])
FAIL_COUNTER = Counter(
    "black_box_test_failures_total",
    "Total count of test run failures. "
    "At least one test failure counts "
    "as the whole run failing.",
    ["plugin"],
)


class Plugin:
    def __init__(self, name, marker=None):
        self.name = name
        self.last_start = 0.0
        marker = f" -m {marker}" if marker else ""
        ibutsu_server = f" -o ibutsu_server={config.IBUTSU_SERVER}" if config.IBUTSU_SERVER else ""
        ibutsu_src = f" -o ibutsu_source={config.IBUTSU_SOURCE}" if config.IBUTSU_SOURCE else ""
        self.run_args = shlex.split(
            f"tests plugin {name}{marker}{ibutsu_server}{ibutsu_src} -s -v --color=no"
        )
        self.runs = RUN_COUNTER.labels(plugin=self.name)
        self.failures = FAIL_COUNTER.labels(plugin=self.name)
        self.duration = DURATION_COUNTER.labels(plugin=self.name)
        self.last_start = 0.0
        self.last_completion = 0.0

        self.env = os.environ.copy()
        # Pass configuration into IQE via env var (instead of using a settings.local.yaml)
        main_opts = {
            "username": config.IQE_USERNAME,
            "password": config.IQE_PASSWORD,
            "identity": {"account_number": config.IQE_ACCT_NO},
        }
        users_opts = {
            "primary_user": {
                "username": config.IQE_USERNAME,
                "password": config.IQE_PASSWORD,
                "identity": {"account_number": config.IQE_ACCT_NO},
            }
        }
        self.env.update(
            {
                "MERGE_ENABLED_FOR_DYNACONF": "true",
                "ENV_FOR_DYNACONF": config.ENV_FOR_DYNACONF,
                "IQE_TESTS_LOCAL_CONF_PATH": config.IQE_TESTS_LOCAL_CONF_PATH,
                "DYNACONF_MAIN": f"@json {json.dumps(main_opts)}",
                "DYNACONF_USERS": f"@json {json.dumps(users_opts)}",
            }
        )

    def update_env(self, key, val):
        self.env.update({key: val})

    def _out(self, line):
        log.debug(" |out| [%s] %s", self.name, line.rstrip())

    def _cmd_done(self, cmd, success, __):
        self.last_completion = time.time()
        duration = self.last_completion - self.last_start
        log.info("[%s] test stopped, took %d sec", self.name, duration)
        self.runs.inc()
        self.duration.inc(duration)
        if not success:
            self.failures.inc()
            log.error("[%s] test output:\n%s", self.name, cmd.stdout.decode("utf-8"))
            log.error("******** %s: failure ********", self.name)

    def run_test(self):
        # Uncomment if debugging and you want to check the value of the creds...
        """
        sh.iqe(
            "debug", "keysearch", "main", _env=self.env, _out=self._out, _tee=True, _err_to_out=True
        )
        sh.iqe(
            "debug",
            "keysearch",
            "users",
            _env=self.env,
            _out=self._out,
            _tee=True,
            _err_to_out=True,
        )
        """
        log.info("[%s] starting test with: iqe %s", self.name, " ".join(self.run_args))

        self.last_start = time.time()
        time.sleep(1)

        try:
            sh.iqe(
                *self.run_args,
                _env=self.env,
                _out=self._out,
                _done=self._cmd_done,
                _tee=True,
                _err_to_out=True,
            )
        except sh.ErrorReturnCode:
            # Let the done callback handle errors
            pass


class IqeRunner(threading.Thread):
    def __init__(self, runner_name, plugin_configs, pod_mgr=None):
        super().__init__()
        self.name = runner_name
        self.daemon = True
        self.plugins = [Plugin(*cfg) for cfg in plugin_configs]
        self.pod_mgr = pod_mgr
        self.stop_event = threading.Event()
        self.proc = None
        log.info("assigned plugins: %s", [", ".join(p.name for p in self.plugins)])

    def reserve_pod(self, plugin):
        ip, pod = self.pod_mgr.reserve_pod()
        log.debug("[%s] reserved pod '%s'", plugin.name, pod.name)
        opts = {"command_executor": f"http://{ip}:4444/wd/hub"}
        plugin.update_env("DYNACONF_BROWSER", f"@json {json.dumps(opts)}")
        return pod

    def run_plugin(self, plugin):
        try:
            pod = self.reserve_pod(plugin)
        except PodsNotAvailable:
            log.error("[%s] no pods are free ... skipping this test run", plugin.name)
            return

        try:
            plugin.run_test()
        finally:
            if self.pod_mgr:
                self.pod_mgr.release_pod(pod)
                log.debug("[%s] released pod '%s'", plugin.name, pod.name)

    @staticmethod
    def _delay_passed(plugin):
        log.debug("[%s] plugin last completion: %f", plugin.name, plugin.last_completion)
        passed = plugin.last_completion + config.RUN_DELAY < time.time()
        log.debug("[%s] plugin delay passed: %s", plugin.name, passed)
        return passed

    def run(self):
        while not self.stop_event.is_set():
            for plugin in self.plugins:
                if not plugin.last_completion or self._delay_passed(plugin):
                    self.run_plugin(plugin)
                else:
                    log.debug("[%s] skipping due to time delay", plugin.name)
            time.sleep(1)

    def stop(self):
        self.stop_event.set()
