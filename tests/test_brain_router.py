import unittest
import httpx
from unittest.mock import patch, AsyncMock

try:
    from engine.network_router import BrainRouter
except ImportError:
    BrainRouter = None


class TestBrainRouter(unittest.IsolatedAsyncioTestCase):
    async def test_import_exists(self):
        """Fail if BrainRouter class is not implemented."""
        self.assertIsNotNone(BrainRouter, "BrainRouter class not found / not implemented yet")

    async def test_ping_remote_offline(self):
        """Verify unreachable host returns 'Offline'."""
        if not BrainRouter:
            self.skipTest("No BrainRouter")

        router = BrainRouter()
        # Mock httpx.AsyncClient.get to raise a connection error
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")

            status = await router.ping_remote()
            self.assertEqual(status, 'Offline')

    async def test_get_primary_host_fallback(self):
        """Verify routing falls back to local if remote is down."""
        if not BrainRouter: self.skipTest("No BrainRouter")
        
        router = BrainRouter()
        # Manually set state
        router.status['remote'] = False
        
        host = router.get_primary_host('reflection')
        self.assertEqual(host, "http://localhost:11434", "Should fallback to localhost")

    async def test_get_primary_host_remote(self):
        """Verify routing uses remote if online for reflection."""
        if not BrainRouter: self.skipTest("No BrainRouter")
        
        router = BrainRouter()
        router.status['remote'] = True
        
        host = router.get_primary_host('reflection')
        self.assertEqual(host, "http://192.168.0.69:11434", "Should use Librarian IP")

if __name__ == '__main__':
    unittest.main()
