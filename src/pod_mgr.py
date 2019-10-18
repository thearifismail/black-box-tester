import logging
import threading
import time

from ocdeployer.utils import get_json
from ocdeployer.utils import oc
from ocdeployer.utils import wait_for_ready


log = logging.getLogger("blackbox.pod_mgr")
lock = threading.Lock()


class PodNotFound(Exception):
    def __init__(self, name, message):
        super().__init__(message)
        self.name = name


class PodsNotAvailable(Exception):
    pass


class SeleniumPod:
    """
    Represents a single selenium pod which can be reserved by a test.
    """

    @classmethod
    def get_all(cls):
        selenium_pods = get_json("pod", label="app=selenium")
        return [
            cls(pod["metadata"]["name"])
            for pod in selenium_pods["items"]
            if pod["status"]["phase"] == "Running"
        ]

    def __init__(self, name):
        self.name = name
        self.in_use = False

    def __str__(self):
        return self.name

    def get_json(self):
        data = get_json("pod", self.name)
        if not data:
            raise PodNotFound(self.name, f"pod {self.name} no longer exists")
        return data

    def get_ip(self):
        return self.get_json()["status"].get("podIP")


class SeleniumPodMgr:
    """
    Keeps track of all selenium pods and allows test to reserve/release a pod.

    A pod's IP is looked up each time it is reserved.

    If a pod is found to no longer exist, we run a reconciliation to update the
    list of pods available for tests to reserve.
    """

    def __init__(self):
        self.pods = SeleniumPod.get_all()
        self.expected_num_pods = 0

    @staticmethod
    def _pod_names(pod_list):
        return [pod.name for pod in pod_list]

    def reconcile_pods(self):
        log.info("reconciling pods")

        latest_pods = SeleniumPod.get_all()

        missing_pods = [pod for pod in self.pods if pod.name not in self._pod_names(latest_pods)]
        new_pods = [pod for pod in latest_pods if pod.name not in self._pod_names(self.pods)]
        log.info(
            "found %d missing pods: %s", len(missing_pods), ", ".join(self._pod_names(missing_pods))
        )
        log.info("found %d new pods: %s", len(new_pods), ", ".join(self._pod_names(new_pods)))

        for pod in missing_pods:
            self.pods.remove(pod)
        self.pods.extend(new_pods)

    def scale_selenium_pods(self, num):
        """
        Create the desired number of selenium pods
        """
        oc("scale", "dc/selenium", f"--replicas={num}")
        wait_for_ready("dc", "selenium")
        self.expected_num_pods = num
        self.reconcile_pods()

    def get_free_pod(self):
        # Check to see if any pods have switched to/from 'running' state
        # since the last reconcile
        if len(self.pods) != self.expected_num_pods:
            self.reconcile_pods()
            time.sleep(0.5)
            return self.get_free_pod()

        for pod in self.pods:
            if not pod.in_use:
                return pod
        else:
            raise PodsNotAvailable()

    def reserve_pod(self):
        with lock:
            try:
                pod = self.get_free_pod()
                ip = pod.get_ip()
            except PodNotFound as err:
                log.warning("pod '%s' no longer exists", err.name)
                self.reconcile_pods()
                pod = self.get_free_pod()
                ip = pod.get_ip()

            pod.in_use = True
            log.debug(
                "pod '%s' reserved, %d/%d pods available",
                pod.name,
                len([p for p in self.pods if not p.in_use]),
                len(self.pods),
            )
            return ip, pod

    def release_pod(self, pod):
        with lock:
            pod.in_use = False
            log.debug(
                "pod '%s' released, %d/%d pods available",
                pod.name,
                len([p for p in self.pods if not p.in_use]),
                len(self.pods),
            )
