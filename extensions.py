from maltego_trx.decorator_registry import TransformRegistry

registry = TransformRegistry(
        owner="Netragard",
        author="Dan Staples <dstaples@netragard.com>",
        host_url="http://localhost:8080",
        seed_ids=["sherlock"]
)

# metadata
registry.version = "0.1"

# transform suffix to indicate datasource
registry.display_name_suffix = " [Sherlock]"
