import os

import dotenv
from unittest import mock

from daily_read import ngi_data, config

dotenv.load_dotenv()


####################################################### TESTS #########################################################


def test_create_project_data_master(data_repo_full):
    """With existing git repo, test creation of a ProjectDataMaster class"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert len(data_master.sources) == 3
    assert data_master.source_names == ["NGI Stockholm", "SNP&SEQ", "Uppsala Genome Center"]
    assert data_master._data_saved == False
    assert data_master._data_fetched == False


def test_create_project_data_master_no_commit(data_repo_no_commit):
    """With existing git repo but without commits, test creation of a ProjectDataMaster class"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert len(data_master.sources) == 3
    assert data_master.source_names == ["NGI Stockholm", "SNP&SEQ", "Uppsala Genome Center"]
    assert data_master._data_saved == False
    assert data_master._data_fetched == False

    assert data_master.data_repo.commit().message == "Empty file as a first commit"


def test_modified_or_new_no_commit(data_repo_no_commit):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert not data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 0


def test_modified_or_new(data_repo_full):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 11


def test_modified_or_new_untracked(data_repo_untracked):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "untracked_file" in file_names[0]


def test_modified_or_new_staged(data_repo_new_staged):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 5
    assert any("staged_file" in s for s in file_names)


def test_modified_or_new_modified_not_staged(data_repo_modified_not_staged):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "modified_file" in file_names[0]


def test_modified_or_new_modified_staged(data_repo_modified_staged):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "modified_staged_file" in file_names[0]


def test_modified_or_new_tracked(data_repo_tracked):
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)

    assert not data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]

    assert len(set(file_names)) == 0


# Planned tests #


def test_getting_data():
    # Test getting data
    # When everything is ok
    # When some source fails
    # When all sources fails
    # When some source is not enabled
    # When no source is enabled
    FETCH_FROM_NGIS = os.getenv("DAILY_READ_FETCH_FROM_NGIS")
    FETCH_FROM_SNPSEQ = os.getenv("DAILY_READ_FETCH_FROM_SNPSEQ")
    FETCH_FROM_UGC = os.getenv("DAILY_READ_FETCH_FROM_UGC")
    pass


# Test saving data

# Test add data for staging
# If other things are added already
# Test adding something that isn't changed

# Test commit staged data
# Make sure everything staged is committed
# and nothing else
# If nothing is added to stage
