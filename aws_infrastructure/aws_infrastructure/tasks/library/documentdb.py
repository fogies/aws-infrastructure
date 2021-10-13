from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
import os
from pathlib import Path
import ruamel.yaml
import shutil
from typing import List
from typing import Union


class DocumentDBConfig:
    """
    Configuration for connection to a DocumentDB instance.
    """

    _admin_password: str
    _admin_user: str
    _endpoint: Path
    _hosts: List[str]
    _port: int

    def __init__(self, *, admin_user: str, admin_password: str, endpoint:str, hosts: List[str], port: int):
        self._admin_user = admin_user
        self._admin_password = admin_password
        self._endpoint = endpoint
        self._hosts = hosts
        self._port = port

    @staticmethod
    def load(documentdb_config_path: Path):
        with open(documentdb_config_path) as documentdb_config_file:
            yaml_config = ruamel.yaml.safe_load(documentdb_config_file)

        return DocumentDBConfig(
            admin_user = yaml_config['admin_user'],
            admin_password = yaml_config['admin_password'],
            endpoint = yaml_config['endpoint'],
            hosts = yaml_config['hosts'],
            port = yaml_config['port'],
        )

    @property
    def admin_password(self) -> str:
        return self._admin_password

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def hosts(self) -> List[str]:
        return self._hosts

    @property
    def port(self) -> int:
        return self._port


def _destroy_post_exec(
    *,
    terraform_dir: Path,
    config_dir: Path,
):
    """
    Create a helper function for the destroy task.
    """

    def delete_empty_config_dir(
        *,
        context,
        params,
    ):
        """
        Delete any instance directories which are effectively empty.
        """

        # Terraform will create directories for created files.
        # But Terraform will not automatically remove those same directories, even if they are empty.
        # Look for these directories, delete them if they are effectively empty.
        if config_dir.exists() and config_dir.is_dir():
            # Some children may exist but can be safely deleted.
            # Check if all existing children are known to be safe to delete.
            # If so, delete everything. Otherwise, leave everything.
            safe_to_delete_entries = [
                # Not expecting any children
            ]

            # Determine if all existing files are safe to delete
            existing_entries = os.scandir(config_dir)
            unknown_entries = [
                entry_current
                for entry_current in existing_entries
                if entry_current.name not in safe_to_delete_entries
            ]

            # If everything is safe to delete, then go ahead with deletion
            if len(unknown_entries) == 0:
                shutil.rmtree(config_dir)

    return delete_empty_config_dir


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
    name: str,

    terraform_variables_factory=None,
    terraform_variables_path: Union[Path, str] = None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)
    terraform_variables_path = Path(terraform_variables_path) if terraform_variables_path else None

    ns_documentdb = Collection('documentdb')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        output_tuple_factory=namedtuple(
            'documentdb',
            [
                'admin_user',
                'admin_password',
                'endpoint',
                'hosts',
            ]
        ),

        terraform_variables_factory=terraform_variables_factory,
        terraform_variables_path=terraform_variables_path,
        destroy_post_exec=_destroy_post_exec(
            terraform_dir=terraform_dir,
            config_dir=Path(terraform_dir, name),
        ),
    )

    compose_collection(
        ns_documentdb,
        ns_terraform,
        sub=False
    )

    return ns_documentdb


def create_documentdb_read_only(
    ns_documentdb: Collection,
):
    """
    Create a read only context manager.
    """

    documentdb_read_only = aws_infrastructure.tasks.library.terraform.create_context_manager_read_only(
        init=ns_documentdb.tasks['init'],
        output=ns_documentdb.tasks['output'],
    )

    return documentdb_read_only
