# Examples

A Summer Camp application, the shape the rules in `oss_portal_domain_driven.md` produce. `summer-camp-service` is the
bounded context (the pack, §3.1); `camp-application` is one aggregate inside it.

```
src/
  summer-camp-service/
    summer-camp-service-app.ts            ← Cloud Run boot, internal ingress
    summer-camp-service-proxy/            ← Apigee proxy for /v1/summer-camp/**, standard policy chain
    migrations/
      0007-expand-add-seat-preference.sql ← additive only
    camp-application/
      camp-application.ts                 ← CampApplication, Applicant, ApplicationSubmitted, CampApplicationRepository
      camp-application-service.ts         ← CampApplicationService, CampApplicationRepositorySql
      camp-application-service-routes.ts  ← POST /v1/summer-camp/camp-applications
      camp-application-bff.ts             ← CampApplicationBff (destination), CampApplicationGateway
      camp-application-bff-routes.ts      ← POST /bff/camp-applications
      camp-application-client.ts          ← CampApplicationClient
      camp-application-paths.ts           ← /summer-camp/apply, /summer-camp/applied
      apply-for-camp.view.ts              ← ApplyForCampView
      application-received.view.ts        ← ApplicationReceivedView

packages/citizen-portal-app/
  server.ts                               ← Angular SSR + BFF; mounts camp-application-bff-routes
  citizen/                                ← citizen portal router and shell
```

Submitting an application: `ApplyForCampView` renders `CampApplicationClient`; submit posts to the BFF route with the
session cookie; `CampApplicationBff` calls `/v1/summer-camp/camp-applications` through Apigee with the citizen's token;
`CampApplicationService.submit` updates the root through `CampApplicationRepositorySql` and publishes
`ApplicationSubmitted` to Pub/Sub for the confirmation email; `CampApplicationBff.destination` returns
`/summer-camp/applied`.

The application's attachments (proof of age, say) go to Cloud Storage; the database keeps their object references.
Registering the aggregate adds nothing to the service inventory, because `summer-camp-service` is already there, but a
new publishing aggregate adds its dead-letter depth alert (§6.3).
