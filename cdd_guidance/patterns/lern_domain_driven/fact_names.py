"""The name of each fact the LERN overlay records on a node and the LERN rules read, written once so a writer and a
reader cannot spell one differently."""

# A NodeRoot's store-reading repositories, the repository instances the test setup never resets, and the posted-body
# reads no schema parses.
NODE_REPOSITORIES = "node_repositories"
UNRESET_INSTANCES = "unreset_instances"
UNPARSED_BODY_READS = "unparsed_body_reads"
# A Route's body reads no schema checks.
LOOSE_BODY_READS = "loose_body_reads"
# How a NodeRoot or a Route answers an error: throws of a bare object or string, and error statuses it replies with.
AD_HOC_THROWS = "ad_hoc_throws"
ERROR_REPLIES = "error_replies"
# An aggregate's request reads in its framework-free core, and the browser paths it writes outside its paths module.
CORE_REQUEST_READS = "core_request_reads"
WEB_PATH_LITERALS = "web_path_literals"
# A behavior file's reach into a tier, whether it runs the shared behaviors, and what it stubs.
TIER_REACHES = "tier_reaches"
RUNS_SHARED_BEHAVIOR = "runs_shared_behavior"
STUBS = "stubs"
STUBBED_REQUESTS = "stubbed_requests"
# A story test file's context casts, givens that assert, helpers that wrap the domain, hand-written outline entries,
# and the screen stories it describes.
CONTEXT_CASTS = "context_casts"
ASSERTING_GIVENS = "asserting_givens"
DOMAIN_WRAPPING_HELPERS = "domain_wrapping_helpers"
HAND_WRITTEN_ENTRIES = "hand_written_entries"
SCREEN_STORIES = "screen_stories"
# Whether a story has a screen story file that drives it.
HAS_SCREEN_STORY = "has_screen_story"
