import json
import logging
import os

log = logging.getLogger(__name__)


class ProjectDataMaster(object):
    def __init__(self, config, sources):
        self.config = config
        self.sources = sources
        self.source_names = [source.name for source in sources]
        self.__data_fetched = False

    def get_data(self):
        for source in self.sources:
            try:
                source.get_data()
            except Exception as e:
                log.error(f"Failed to fetch data from {source.name}")
                log.exception(e)
                raise

        self.__data_fetched = True

    def save_data(self):
        assert self.__data_fetched
        data_location = self.config.DATA_LOCATION
        if not os.path.isdir(data_location):
            raise ValueError(f"Data Location is not a directory: {data_location}")

        for source in self.sources:
            source_dir = os.path.join(data_location, source.dirname)
            if not os.path.exists(source_dir):
                os.mkdir(source_dir)
            if not os.path.isdir(source_dir):
                raise ValueError(
                    f"Failed to use data directory {source_dir} for download, path exists but is not a directory."
                )
            # Save individual projects to json files
            for project_id, project_data in source.data.items():
                file_name = os.path.join(source_dir, project_id + ".json")
                with open(file_name, mode="w") as fh:
                    log.debug(f"Writing data for {project_id} to {file_name}")
                    fh.write(json.dumps(project_data))

    def get_modified_projects(self):
        # TODO Here go git stuff
        return ["orderportal_id2", "orderportal_id3"]

    def stage_data_for_project(self, project_id):
        pass

    def commit_staged_data(self, message):
        pass


class StockholmProjectData(object):
    """NGIProjectData subclass for NGI Stockholm data"""

    def __init__(self, config):
        super().__init__(config)
        self.name = "NGI Stockholm"
        self.dirname = "ngi_stockholm"

    def get_data(self, project_id=None):
        pass


class SNPSEQProjectData(object):
    """NGIProjectData subclass for NGI SNP&SEQ data"""

    def get_data(self, project_id=None):
        pass


class UGCProjectData(object):
    """NGIProjectData subclass for NGI UGC data"""

    def get_data(self, project_id=None):
        pass
