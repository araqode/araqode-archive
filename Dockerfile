# araqode-archive
# A curated, multi-modal dataset

FROM scratch

COPY ./dataset /araqode-archive
VOLUME /araqode-archive

# Set a default command that does nothing but exits successfully.
# This ensures the container doesn't try to run an application when started,
# as its purpose is just to hold data.
CMD ["true"]
