# Ingress-CRD

Configures CRDs expected by the Ingress chart.

- Configures cert-manager CRDs published as part of releases:

  <https://cert-manager.io/docs/installation/kubernetes/>
  
- Configures Traefik CRDs taken from a specific version of its chart.

  <https://github.com/traefik/traefik-helm-chart/tree/master/traefik>
  
Only one release may be installed, because this creates global resources that may conflict.

## Versions

### 0.1.0

- Initial version, cert-manager from 1.1.0 and Traefik from 9.12.3.
