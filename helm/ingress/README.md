# Ingress

Configures a basic ingress environment:

- Configures Traefik using its chart:

  <https://github.com/traefik/traefik-helm-chart/tree/master/traefik>

## Requirements
  
Only one release may be installed, because this creates global resources that may conflict.

Assumes prior installation of ingress-crd.

## Versions

### 0.7.0

- For use via Helmfile with ingress-crd 0.5.0 and cert-manager 1.6.1.
- Remove class filters from LetsEncrypt solvers.
  Traefik was not detecting Ingress created by cert-manager.
- Remove abandoned references to cert-manager in values.yaml.

### 0.6.0

- Remove explicit namespaces from resources.
  This should instead be managed via Helmfile.
- Enable allowCrossNamespace.

### 0.5.0

- Remove cert-manager as dependency. 
  It should instead be managed via Helmfile.
- Increment dependency versions, Traefik to 10.6.1.

### 0.4.0

- Renamed a `private` entrypoint on port 8000.

### 0.3.0

- Create a `dashboard` entrypoint on port 8000.

### 0.2.0

- Refactor CRDs into separate chart ingress-crd.
  Install would fail because those were not yet available.
  Separation is also recommended (<https://helm.sh/docs/chart_best_practices/custom_resource_definitions/>).
- Increment dependency versions, cert-manager to 1.1.0 and Traefik to 9.12.3.

### 0.1.0

- Initial version.
