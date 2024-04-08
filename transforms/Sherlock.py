import sys
import logging
from os import path
from extensions import registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform, UIM_TYPES
from maltego_trx.transform import DiscoverableTransform

sys.path.append(path.join(path.dirname(path.dirname( path.abspath(__file__))), "sherlock", "sherlock"))
from sherlock import sherlock
from result import QueryStatus
from notify import QueryNotify
from sites import SitesInformation

# Global variable to count the number of results.
count = 0

# Prevent urllib3 from spamming debug logs
logging.getLogger("urllib3").setLevel(logging.WARNING)


class QueryNotifyMaltego(QueryNotify):
    def __init__(self, response, result=None, print_all=True):
        super().__init__(result)
        self.response = response
        self.print_all = print_all

    def start(self, message):
        self.response.addUIMessage(f'[*] Checking username {message} with sherlock')
    
    def update(self, result):
        self.result = result
        if result.status == QueryStatus.CLAIMED:
            self.countResults()
            self.response.addUIMessage(f'[+] {result.site_name}: {result.site_url_user}')
        elif result.status == QueryStatus.AVAILABLE:
            if self.print_all:
                self.response.addUIMessage(
                    f'[-] {result.site_name}: Not found!',
                    UIM_TYPES['debug']
                )
        elif result.status == QueryStatus.UNKNOWN:
            if self.print_all:
                self.response.addUIMessage(
                    f'[-] {result.site_name}: {result.context}',
                    UIM_TYPES['debug']
                )
        elif result.status == QueryStatus.ILLEGAL:
            if self.print_all:
                self.response.addUIMessage(
                    f'[-] {result.site_name}: Illegal Username Format For This Site!',
                    UIM_TYPES['partial']
                )
        else:
            self.response.addUIMessage(
                f'Unknown query status {result.status} for site {result.site_name}',
                UIM_TYPES['partial']
            )
    
    def finish(self, message=None):
        self.response.addUIMessage(f'[*] Search completed with {self.countResults() - 1} results')
    
    def countResults(self):
        global count
        count += 1
        return count


@registry.register_transform(display_name="To Social Media Accounts",
                             input_entity="maltego.Alias",
                             description='Hunt down social media accounts by username across social networks',
                             output_entities=["maltego.Affiliation"])
class Sherlock(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        username = request.Value

        sites = SitesInformation(
            path.join(path.dirname(path.dirname(__file__)), 'sherlock', 'sherlock', 'resources', 'data.json')
        )
        sites.remove_nsfw_sites()
        site_data = {site.name: site.information for site in sites}

        results = sherlock(
            username,
            site_data,
            QueryNotifyMaltego(response)
        )

        for website_name, result in results.items():
            if result.get("status").status == QueryStatus.CLAIMED:
                entity = response.addEntity('maltego.affiliation', website_name)
                entity.addProperty('affiliation.network', displayName='Network', value=website_name)
                entity.addProperty('affiliation.uid', displayName='UID', value=username)
                entity.addProperty('affiliation.profile-url', displayName='Profile URL', value=result['url_user'])
