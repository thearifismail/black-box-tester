# Get centos base image
# Use FROM scratch for blank image
FROM docker.io/centos/python-36-centos7

# who are you
MAINTAINER aarif

COPY requirements.txt /
CMD ["ls -l /"]

# Run when creating image
RUN pip install --no-cache-dir -r /requirements.txt

# copy file into place
# COPY cachet_update_daemon.py / 
COPY update_cachet.py /

# Expose the port
EXPOSE 10000

# Arif's project
ENV CACHET_HOSTNAME "${CACHET_HOSTNAME}"
ENV CACHET_TOKEN "${CACHET_TOKEN}"
ENV CACHET_USERNAME "${CACHET_USERNAME}"
ENV CACHET_PASSWORD "${CACHET_PASSWORD}"
# Cachet for production cluster
ENV INSIGHTS_USERNAME "${INSIGHTS_USERNAME}"
ENV INSIGHTS_PASSWORD "${INSIGHTS_PASSWORD}"
ENV INSIGHTS_SERVER "${INSIGHTS_SERVER}"
ENV PYTHONWARNINGS "${PYTHONWARNINGS}"


# Executed once image is up / container is created
CMD ["ls -l /"]
CMD ["python", "/update_cachet.py"]