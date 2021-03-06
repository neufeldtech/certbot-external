"""ExternalDVSNI"""
import logging

from certbot import errors
from certbot.plugins import common

logger = logging.getLogger(__name__)


class ExternalDvsni(common.TLSSNI01):
    """Class performs DVSNI challenges within the External configurator.

    :ivar configurator: ExternalConfigurator object
    :type configurator: :class:`~configurator.ExternalConfigurator`

    :ivar list achalls: Annotated tls-sni-01
        (`.KeyAuthorizationAnnotatedChallenge`) challenges.

    :param list indices: Meant to hold indices of challenges in a
        larger array. ExternalDvsni is capable of solving many challenges
        at once which causes an indexing issue within ExternalConfigurator
        who must return all responses in order.  Imagine ExternalConfigurator
        maintaining state about where all of the http-01 Challenges,
        Dvsni Challenges belong in the response array.  This is an optional
        utility.

    :param str challenge_conf: location of the challenge config file

    """

    def perform(self):
        """Perform a DVSNI challenge using an external script.

        :returns: list of :class:`certbot.acme.challenges.DVSNIResponse`
        :rtype: list

        """
        if not self.achalls:
            return []

        # Create challenge certs
        responses = [self._setup_challenge_cert(x) for x in self.achalls]

        for achall in self.achalls:
            ret = self.configurator.call_handler("perform",
                domain = achall.domain,
                z_domain = achall.response(achall.account_key).z_domain,
                cert_path = self.get_cert_path(achall),
                key_path = self.get_key_path(achall),
                port = str(self.configurator.config.tls_sni_01_port)
            )

            if ret in (None, NotImplemented):
                raise errors.PluginError("perform handler failed")

        return responses

