# Ingress

Configures a basic ingress environment:

- Configures cert-manager using its chart:

  <https://github.com/jetstack/cert-manager/tree/master/deploy/charts/cert-manager>
  
- Configures Traefik using its chart:

  <https://github.com/traefik/traefik-helm-chart/tree/master/traefik>

## Requirements
  
Only one release may be installed, because this creates global resources that may conflict.

Assumes prior installation of ingress-crd.

## Versions

### 0.4.0

- Create a `private` entrypoint on port 8000.
- Move `dashboard` entrypoint to port 9000.

### 0.3.0

- Create a `dashboard` entrypoint on port 8000.

### 0.2.0

- Refactor CRDs into separate chart ingress-crd.
  Install would fail because those were not yet available.
  Separation is also recommended (<https://helm.sh/docs/chart_best_practices/custom_resource_definitions/>).
- Increment dependency versions, cert-manager to 1.1.0 and Traefik to 9.12.3.

### 0.1.0

- Initial version.
