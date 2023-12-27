import os

import dotenv
import git
import pytest
import json

from daily_read import ngi_data, config

dotenv.load_dotenv()


def _create_all_files(file_list, data_location):
    """Helper method to create files in file_list inside data_location"""
    for file_relpath in file_list:
        file_path = os.path.join(data_location, file_relpath)
        os.makedirs(os.path.split(file_path)[0], exist_ok=True)
        with open(file_path, "w") as fh:
            fh.write(
                json.dumps(
                    {
                        "orderer": "dummy@dummy.se",
                        "project_dates": {
                            "2023-06-15": ["Samples Received"],
                            "2023-06-28": ["Reception Control finished", "Library QC finished"],
                        },
                        "internal_id": "P123456",
                        "internal_name": "D.Dummysson_23_01",
                    }
                )
            )


####################################################### FIXTURES #########################################################


@pytest.fixture
def data_repo(tmp_path):
    data_location = os.path.join(tmp_path, "git_repo")
    os.environ["DAILY_READ_DATA_LOCATION"] = str(data_location)
    os.mkdir(data_location)
    data_repo = git.Repo.init(data_location)

    # Need an empty commit to be able to do "repo.index.diff("HEAD")"
    new_file_path = os.path.join(data_location, ".empty")
    open(new_file_path, "a").close()
    data_repo.index.add([new_file_path])
    data_repo.index.commit("Empty file from tests as a first commit")

    return data_repo


@pytest.fixture
def data_repo_no_commit(tmp_path):
    data_location = os.path.join(tmp_path, "git_repo")
    os.environ["DAILY_READ_DATA_LOCATION"] = str(data_location)
    os.mkdir(data_location)
    data_repo = git.Repo.init(data_location)
    return data_repo


@pytest.fixture
def data_repo_untracked(data_repo):
    """Adds two untracked files."""
    untracked_files = ["NGIS/2023/untracked_file1.json", "UGC/2022/untracked_file2.json"]
    _create_all_files(untracked_files, data_repo.working_dir)

    return data_repo


@pytest.fixture
def data_repo_new_staged(data_repo):
    """Adds two new files to the index to be committed."""
    staged_files = ["NGIS/2023/staged_file1.json", "UGC/2023/staged_file2.json"]
    _create_all_files(staged_files, data_repo.working_dir)
    data_repo.index.add(staged_files)

    return data_repo


@pytest.fixture
def data_repo_modified_not_staged(data_repo):
    """Adds two previously committed files with new modifications that is not staged to be committed."""
    modified_not_staged_files = ["SNPSEQ/2023/modified_file1.json", "NGIS/2021/modified_file2.json"]
    _create_all_files(modified_not_staged_files, data_repo.working_dir)
    data_repo.index.add(modified_not_staged_files)
    # Check that nothing else is committed by mistake
    assert len(data_repo.index.diff("HEAD")) == len(modified_not_staged_files)
    data_repo.index.commit("Commit Message")

    for file_relpath in modified_not_staged_files:
        file_path = os.path.join(data_repo.working_dir, file_relpath)
        with open(file_path) as fh:
            json_list = json.load(fh)
        json_list["project_dates"].update({"2023-07-09": ["All Samples Sequenced"]})
        with open(file_path, "w") as fh:
            fh.write(json.dumps(json_list))

    return data_repo


@pytest.fixture
def data_repo_modified_staged(data_repo):
    """Adds two previously committed files with new modifications that is staged to be committed."""
    modified_not_staged_files = ["SNPSEQ/2022/modified_staged_file1.json", "NGIS/2020/modified_staged_file2.json"]
    _create_all_files(modified_not_staged_files, data_repo.working_dir)
    data_repo.index.add(modified_not_staged_files)
    data_repo.index.commit("Commit Message")

    for file_relpath in modified_not_staged_files:
        file_path = os.path.join(data_repo.working_dir, file_relpath)
        with open(file_path) as fh:
            json_list = json.load(fh)
        json_list["project_dates"].update({"2023-07-09": ["All Samples Sequenced"]})
        with open(file_path, "w") as fh:
            fh.write(json.dumps(json_list))

    return data_repo


@pytest.fixture
def data_repo_tracked(data_repo):
    """Adds three tracked files to the repository"""
    tracked_files = ["SNPSEQ/2022/tracked_file1.json", "UGC/2022/tracked_file2.json", "NGIS/2021/tracked_file3.json"]
    _create_all_files(tracked_files, data_repo.working_dir)
    data_repo.index.add(tracked_files)
    # Make sure nothing else is committed by mistake
    assert len(data_repo.index.diff("HEAD")) == len(tracked_files)
    data_repo.index.commit("Commit Message")

    return data_repo


@pytest.fixture
def data_repo_full(
    data_repo_untracked,
    data_repo_modified_not_staged,
    data_repo_tracked,
    data_repo_modified_staged,
    data_repo_new_staged,
):
    """Represents a data repository with all five different kinds of files.

    Note that the order of the fixtures matter since commits cannot be made if staged files exist.
    So files are staged in the final fixtures only.
    """
    return data_repo_new_staged


####################################################### TESTS #########################################################


def test_create_project_data_master(data_repo_full):
    """With existing git repo, test creation of a ProjectDataMaster class"""
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert len(data_master.sources) == 3
    assert data_master.source_names == ["NGI Stockholm", "SNP&SEQ", "Uppsala Genome Center"]
    assert data_master._data_saved == False
    assert data_master._data_fetched == False


def test_create_project_data_master_no_commit(data_repo_no_commit):
    """With existing git repo but without commits, test creation of a ProjectDataMaster class"""
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert len(data_master.sources) == 3
    assert data_master.source_names == ["NGI Stockholm", "SNP&SEQ", "Uppsala Genome Center"]
    assert data_master._data_saved == False
    assert data_master._data_fetched == False

    assert data_master.data_repo.commit().message == "Empty file as a first commit"


def test_modified_or_new_no_commit(data_repo_no_commit):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert not data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 0


def test_modified_or_new(data_repo_full):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 8


def test_modified_or_new_untracked(data_repo_untracked):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "untracked_file" in file_names[0]


def test_modified_or_new_staged(data_repo_new_staged):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "staged_file" in file_names[0]


def test_modified_or_new_modified_not_staged(data_repo_modified_not_staged):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "modified_file" in file_names[0]


def test_modified_or_new_modified_staged(data_repo_modified_staged):
    config_values = config.Config()
    data_master = ngi_data.ProjectDataMaster(config_values)

    assert data_master.any_modified_or_new()

    modified_or_new = data_master.get_modified_or_new_projects()
    file_names = [project.relative_path for project in modified_or_new]
    assert len(set(file_names)) == 2

    assert "modified_staged_file" in file_names[0]


def test_modified_or_new_tracked(data_repo_tracked):
    config_values = config.Config()
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
