"""OSS Portal tier rules: the browser, the Backend-for-Frontend, the services, the Apigee proxy, and the migrations —
read from the tier facts the overlay records. Each rule cites the OSS Portal Handover Pack v1.0 section it enforces."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_BROWSER = ("DomainView", "ClientRoot")
_BFF = ("BffRoot", "BffRoute")
_SERVICE = ("ServiceRoot", "ServiceRoute")
_VERSIONED_BASE_PATH = re.compile(r"^/v\d+/[a-z][a-z0-9-]*")


def _hits(node, fact: str, message: str) -> list[str]:
    """One message per [line, found] the node's fact lists, formatted with the node's file, the line, and what was found."""
    return [message.format(file=node.source.file, line=line, found=found) for line, found in node.get_fact(fact, [])]


class BrowserCallsOnlyTheBff(PracticeGraphRule):
    """A client or view calls only the BFF on the portal's own origin; services use internal ingress (§3.2)."""

    slug = "browser-calls-only-the-bff"
    node_types = _BROWSER

    def check(self, node, context) -> list[str]:
        return _hits(node, "gateway_calls", "{file}:{line}: `{found}` calls the gateway or a service from the browser; call the aggregate's BFF route instead.")


class TokensStayOnTheServer(PracticeGraphRule):
    """The browser holds only the session cookie; no bearer token reaches client-side script (§3.2)."""

    slug = "tokens-stay-on-the-server"
    node_types = _BROWSER

    def check(self, node, context) -> list[str]:
        return _hits(node, "token_handling", "{file}:{line}: `{found}` handles a token in the browser; keep the token in the BFF session.")


class ViewsRenderOnly(PracticeGraphRule):
    """A view renders the client it holds and fetches nothing, so server-side rendering produces a complete page (APP-09)."""

    slug = "views-render-only"
    node_types = ("DomainView",)

    def check(self, node, context) -> list[str]:
        return _hits(node, "view_fetches", "{file}:{line}: `{found}` fetches in a view; put the call on the client and render what it holds.")


class MaintainLayerPurity(PracticeGraphRule):
    """Browser files never import BFF or service files, BFF files never import service files, and the domain core
    imports no framework, so no code or credential ships into the wrong runtime."""

    slug = "maintain-layer-purity"
    node_types = (*_BROWSER, *_BFF, "Aggregate")

    def check(self, node, context) -> list[str]:
        if node.type == "Aggregate":
            return [
                f"{node.source.file}/{node.name}.ts:{line}: imports `{module}`; the domain core stays framework-free."
                for line, module in node.get_fact("framework_imports", [])
            ]
        return _hits(node, "layer_crossings", "{file}:{line}: imports `{found}`, a tier this file's runtime may not reach.")


class BffDecidesNextPage(PracticeGraphRule):
    """Browser paths live in one `*-paths.ts` per aggregate; `{Domain}Bff.destination` and the router import them."""

    slug = "bff-decides-next-page"
    node_types = ("Aggregate",)

    def check(self, node, context) -> list[str]:
        return [
            f"{relative}:{line}: browser path {path!r} is a literal; import it from the aggregate's `*-paths.ts`."
            for relative, line, path in node.get_fact("web_path_literals", [])
        ]


class RepositoryOwnsAggregateLifecycle(PracticeGraphRule):
    """Only `{Domain}RepositorySql` writes SQL; services, routes, and the BFF never do (§3.5)."""

    slug = "repository-owns-aggregate-lifecycle"
    node_types = (*_BFF, *_SERVICE)

    def check(self, node, context) -> list[str]:
        return _hits(node, "sql_outside_repository", "{file}:{line}: `{found}` is SQL outside `{{Domain}}RepositorySql`; move it into the repository.")


class NoCrossServiceTables(PracticeGraphRule):
    """A service never imports another service's code or repository; it calls that service through Apigee (§3.5)."""

    slug = "no-cross-service-tables"
    node_types = _SERVICE

    def check(self, node, context) -> list[str]:
        return _hits(node, "other_service_imports", "{file}:{line}: imports `{found}` from another service; call that service's Apigee path instead.")


class SanitisedErrorsOnly(PracticeGraphRule):
    """A service answers errors with the uniform contract; no stack trace or SQL reaches a client (§3.3)."""

    slug = "sanitised-errors-only"
    node_types = _SERVICE

    def check(self, node, context) -> list[str]:
        return _hits(node, "unsanitised_errors", "{file}:{line}: `{found}` sends a raw error; reply with the error-catalogue contract.")


class PublishEventsFromTheOwningService(PracticeGraphRule):
    """Only the service that owns a transaction publishes its event (APP-07); the browser and the BFF never publish."""

    slug = "publish-events-from-the-owning-service"
    node_types = (*_BROWSER, *_BFF)

    def check(self, node, context) -> list[str]:
        return _hits(node, "event_publishes", "{file}:{line}: `{found}` publishes outside the owning service; publish from `{{Domain}}Service` after the transaction commits.")


class SecretsFromSecretManager(PracticeGraphRule):
    """No credential is written in code; secrets come from Secret Manager at start-up (§2.3, OP-08)."""

    slug = "secrets-from-secret-manager"
    node_types = (*_BROWSER, *_BFF, *_SERVICE)

    def check(self, node, context) -> list[str]:
        return _hits(node, "hardcoded_secrets", "{file}:{line}: a credential is written in code; read it from Secret Manager at start-up.")


class NoPersonalDataInLogs(PracticeGraphRule):
    """Logs carry identifiers and the trace, never personal data (§2.3, OP-15)."""

    slug = "no-personal-data-in-logs"
    node_types = (*_BFF, *_SERVICE)

    def check(self, node, context) -> list[str]:
        return _hits(node, "personal_data_logged", "{file}:{line}: `{found}` logs personal data; log the record identifier and trace only.")


class OneProxyPerService(PracticeGraphRule):
    """Each service's proxy declares its base path (§3.3)."""

    slug = "one-proxy-per-service"
    node_types = ("Proxy",)

    def check(self, node, context) -> list[str]:
        if node.get_fact("base_paths", []):
            return []
        return [f"{node.source.file}: the proxy declares no `<BasePath>`; give it `/v1/<service>`."]


class VersionBreakingChanges(PracticeGraphRule):
    """Every base path carries its major version, so a breaking change is a new version (APP-05)."""

    slug = "version-breaking-changes"
    node_types = ("Proxy",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}: base path {path!r} has no major version; use `/v<n>/<service>`."
            for path in node.get_fact("base_paths", [])
            if not _VERSIONED_BASE_PATH.match(path)
        ]


class StandardPolicyChain(PracticeGraphRule):
    """Every proxy enforces TLS and runs JWT validation, spike arrest, JSON threat protection, error sanitisation, and
    audit logging, with the request policies in the pack's order (§3.3)."""

    slug = "standard-policy-chain"
    node_types = ("Proxy",)
    _ORDER = ("jwt-validation", "spike-arrest", "json-threat-protection")

    def check(self, node, context) -> list[str]:
        messages = [f"{node.source.file}: the proxy has no `{policy}` policy from the standard chain." for policy in node.get_fact("missing_policies", [])]
        if not node.get_fact("tls_enabled", False):
            messages.append(f"{node.source.file}: no target endpoint enables TLS (`<SSLInfo><Enabled>true</Enabled>`).")
        ran = [policy for policy in node.get_fact("policy_order", []) if policy in self._ORDER]
        expected = [policy for policy in self._ORDER if policy in ran]
        if ran != expected:
            messages.append(f"{node.source.file}: the flow runs {', '.join(ran)}; the chain order is {', '.join(expected)}.")
        return messages


class ExpandAndContractMigrations(PracticeGraphRule):
    """Each migration names its step, and an expand step only adds (APP-14)."""

    slug = "expand-and-contract-migrations"
    node_types = ("Migration",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("migration_step", ""):
            return [f"{node.source.file}: the migration's name says neither expand, backfill, nor contract."]
        return _hits(node, "destructive_statements", "{file}:{line}: `{found}` in an expand step; move it to a contract migration released after the old code retires.")
