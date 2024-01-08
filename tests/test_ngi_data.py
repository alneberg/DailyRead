import os

import dotenv
from unittest import mock
import pytest
import logging

from daily_read import ngi_data, config

dotenv.load_dotenv()

LOGGER = logging.getLogger(__name__)

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


def test_get_unique_orderers(data_repo_full):
    """Test getting unique orders in the project data from statusdb"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        data_master.get_data()
        orderers = data_master.find_unique_orderers()
        assert orderers == set(["dummy@dummy.se"])


def test_user_list(data_repo_full, tmp_path, mocked_statusdb_conn_rows):
    """Test getting and reading users from the user list url"""
    config_values = config.Config()
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("dummy@dummy.se\ntest@dummy.se")
    config_values.USERS_LIST_LOCATION = temp_file
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        assert not set(["dummy@dummy.se", "test@dummy.se"]) ^ set(data_master.user_list)

        data_master.sources[0].statusdb_session.rows.return_value = mocked_statusdb_conn_rows
        data_master.get_data()
        data_master.save_data()
        orderers = data_master.find_unique_orderers()
        assert orderers == set(["dummy@dummy.se", "test@dummy.se"])


def test_save_data_to_disk(data_repo_full, mocked_statusdb_conn_rows):
    """Test saving in git repo the data gotten from statusdb"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        data_master.sources[0].statusdb_session.rows.return_value = mocked_statusdb_conn_rows
        data_master.get_data()
        data_master.save_data()
        assert os.path.exists(os.path.join(config_values.DATA_LOCATION, "NGIS/2023/NGI123457.json"))
        assert os.path.exists(os.path.join(config_values.DATA_LOCATION, "NGIS/2023/NGI123458.json"))


def test_get_data_with_project(data_repo_full, mocked_statusdb_conn_rows):
    """Test getting data for a specific order"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        data_master.sources[0].statusdb_session.rows.return_value = mocked_statusdb_conn_rows
        data_master.get_data("NGI123457")
        assert len(data_master.data.keys()) == 1
        assert "NGI123457" in data_master.data


def test_get_data_with_project_unknown(data_repo_full, mocked_statusdb_conn_rows):
    """Test error thrown when the order specified is not found in statusdb"""
    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        data_master.sources[0].statusdb_session.rows.return_value = mocked_statusdb_conn_rows
        with pytest.raises(ValueError, match="Project NGI123 not found in statusdb") as err:
            data_master.get_data("NGI123")


def test_data_loc_not_abs():
    """Test error thrown when given data location is not an absolute path"""
    config_values = config.Config()
    config_values.DATA_LOCATION = "tests/test_data_location"
    with pytest.raises(
        ValueError, match=f"Data location is not an absolute path: {config_values.DATA_LOCATION}"
    ) as err:
        ngi_data.ProjectDataMaster(config_values)


def test_data_loc_not_dir(tmp_path):
    """Test error thrown when data location is not a directory"""
    config_values = config.Config()
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("test")
    config_values.DATA_LOCATION = temp_file
    with pytest.raises(
        ValueError, match=f"Data Location exists but is not a directory: {config_values.DATA_LOCATION}"
    ) as err:
        ngi_data.ProjectDataMaster(config_values)


def test_get_data_with_no_project_dates(data_repo_full, mocked_statusdb_conn_rows, caplog):
    """Test log output when no project dates are found in statusdb for a specifi project"""
    from copy import deepcopy

    config_values = config.Config()
    with mock.patch("daily_read.statusdb.StatusDBSession"):
        data_master = ngi_data.ProjectDataMaster(config_values)
        data_master.sources[0].statusdb_session.rows.return_value = mocked_statusdb_conn_rows
        proj_no_dates = deepcopy(data_master.sources[0].statusdb_session.rows.return_value[0])
        proj_no_dates.value["proj_dates"] = {}
        proj_no_dates.value["portal_id"] = "NGI123459"
        data_master.sources[0].statusdb_session.rows.return_value.append(proj_no_dates)
        with caplog.at_level(logging.INFO):
            data_master.get_data("NGI123459")
            assert len(data_master.data.keys()) == 1
            assert "NGI123459" in data_master.data
            assert "No project dates found for NGI123459" in caplog.text


# Planned tests #


def test_getting_data():
    # When some source fails
    # When all sources fails
    # When some source is not enabled
    # When no source is enabled
    FETCH_FROM_NGIS = os.getenv("DAILY_READ_FETCH_FROM_NGIS")
    FETCH_FROM_SNPSEQ = os.getenv("DAILY_READ_FETCH_FROM_SNPSEQ")
    FETCH_FROM_UGC = os.getenv("DAILY_READ_FETCH_FROM_UGC")
    pass


# Test add data for staging
# If other things are added already
# Test adding something that isn't changed

# Test commit staged data
# Make sure everything staged is committed
# and nothing else
# If nothing is added to stage
