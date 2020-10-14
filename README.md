# AWS Infrastructure

Frequently-used components for maintaining our AWS infrastructure.

# Dependencies and Requirements

Requires [AWS CLI](https://aws.amazon.com/cli/) for interacting with AWS:

  - Download and install AWS CLI:
  
    <https://aws.amazon.com/cli/>

Requires [Terraform](https://www.terraform.io/) for managing AWS infrastructure.

  - Download Terraform CLI:
  
    <https://www.terraform.io/downloads.html>
    
  - Assumes Terraform CLI is available in path.

    - Temporarily assumes `\bin\terraform.exe`.

Requires [Packer](https://www.packer.io/) for creating Amazon Machine Images (AMIs).

  - Download Packer CLI:
    
    <https://www.packer.io/downloads>
    
  - Assumes Packer CLI is available in path. 
  
    - Temporarily assumes `\bin\packer.exe`.
  
Makes extensive use of [Ansible](https://www.ansible.com/) in configuring machines during image creation.

  - Ansible does not support running an Ansible controller on Windows:
  
    - <https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html>  
    - <http://blog.rolpdog.com/2020/03/why-no-ansible-controller-for-windows.html>
     
    Playbooks are therefore executed on the target machine
    using Packer's [ansible-local](https://www.packer.io/docs/provisioners/ansible-local).
