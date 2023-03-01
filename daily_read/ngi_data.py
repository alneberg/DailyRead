import git
import gitdb
import json
import logging
import os

log = logging.getLogger(__name__)


class ProjectDataMaster(object):
    def __init__(self, config, sources):
        self.config = config
        self.sources = sources
        self.source_names = [source.name for source in sources]

        self.data_repo = self.__setup_data_repo()

        self.__data_fetched = False

    def __setup_data_repo(self):
        # Safety check of path
        if not os.path.isabs(data_location):
            raise ValueError(f"Data location is not an absolute path: {data_location}")

        if os.path.exists(data_location) and not os.path.isdir(data_location):
            raise ValueError(f"Data Location exists but is not a directory: {data_location}")

        # This seems to work with both existing git repos, empty directories
        # and non-existing directories
        data_repo = git.Repo.init(data_location)

        # Make sure there is at least 1 commit (ref HEAD exists)
        try:
            self.data_repo.index.diff("HEAD")
        except gitdb.exc.BadName as e:
            # No commit exists yet
            # Make sure no files are staged to be commited
            if any([self.data_repo.is_dirty(), self.data_repo.untracked_files]):
                raise ValueError(
                    f"Data location has no commits but has modifications, "
                    "please commit those or use an empty directory as the data location"
                )

            # Create empty file to include in the commit
            new_file_path = os.path.join(data_location, ".empty")
            open(new_file_path, "a").close()
            self.data_repo.index.add([new_file_path])
            self.index.commit("Added an empty file as a first commit")

        return data_repo

    def get_data(self):
        """Downloads data for each source into memory"""

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

        if self.data_repo.is_dirty() or self.data_repo.untracked_files:
            if self.any_modified_projects():
                log.info("Changes for projects detected prior to fetching data!")
                for project_id, ngi_node in self.get_modified_or_new_projects():
                    log.info(f"{project_id} from {ngi_node} had changes not yet reported.")

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

    def any_modified_or_new(self):
        """Checks if there are modified or new projects and returns True or False.

        True if any of these files are found:
         - Modified and staged
         - Modified but not staged
         - Untracked files

        """

        return any([self.data_repo.is_dirty(), self.data_repo.untracked_files, self.data_repo.diff("HEAD")])

    def get_modified_or_new_projects(self):
        """Need to return files which are either:
        - Modified and staged
        - Modified but not staged
        - Untracked files
        """

        if self.data_repo.is_dirty() or self.data_repo.untracked_files:
            pass  # Might be tricky to find added files? At least when there's no commit already?

        return [("orderportal_id2", "STHLM"), ("orderportal_id3", "STHLM")]

    def stage_data_for_project(self, project_id):
        pass

    def commit_staged_data(self, message):
        pass


class StockholmProjectData(object):
    """Data class for fetching NGI Stockholm data"""

    def __init__(self, config):
        super().__init__(config)
        self.name = "NGI Stockholm"
        self.dirname = "ngi_stockholm"

    def get_data(self, project_id=None):
        pass


class SNPSEQProjectData(object):
    """Data class for fetching NGI SNP&SEQ data"""

    def get_data(self, project_id=None):
        pass


class UGCProjectData(object):
    """Data class for fetching NGI UGC data"""

    def get_data(self, project_id=None):
        pass
