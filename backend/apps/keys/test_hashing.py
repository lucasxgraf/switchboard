import secrets

from django.test import TestCase

from apps.keys.models import ApiKey


class HashingTestCase(TestCase):
    def test_generated_key_cleartext_not_saved(self) -> None:
        api_key = ApiKey.generate_key(name="TestKey")
        raw_key = api_key.raw_key
        reloaded = ApiKey.objects.get(pk=api_key.pk)

        self.assertNotIn(raw_key, reloaded.hash)
        self.assertNotEqual(api_key.hash, raw_key)

    def test_valid_key_found(self) -> None:
        api_key = ApiKey.generate_key(name="TestKey")
        raw_key = api_key.raw_key
        verified_api_key = ApiKey.verify_key(raw_key)

        self.assertIsNotNone(verified_api_key)
        assert verified_api_key is not None
        self.assertEqual(verified_api_key.pk, api_key.pk)

    def test_invalid_key_declined(self) -> None:
        fake_key = f"sk-{secrets.token_urlsafe(32)}"
        result = ApiKey.verify_key(fake_key)

        self.assertIsNone(result)

    def test_deactivated_key_declined(self) -> None:
        pass

    def test_prefix_readable(self) -> None:
        pass
