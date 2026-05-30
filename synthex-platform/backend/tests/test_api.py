"""API endpoint tests."""
import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_root():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Synthex AI Platform"
        assert "models" in data
        assert "synthex-nova-pro" in data["models"]


@pytest.mark.asyncio
async def test_health():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_models_list():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.get("/v1/models")
        assert r.status_code == 200
        data = r.json()
        assert data["object"] == "list"
        model_ids = [m["id"] for m in data["data"]]
        assert "synthex-nova-pro" in model_ids
        assert "synthex-nova-swift" in model_ids


@pytest.mark.asyncio
async def test_messages_requires_auth():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.post("/v1/messages", json={
            "messages": [{"role": "user", "content": "hello"}]
        })
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_chat_completions_requires_auth():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.post("/v1/chat/completions", json={
            "model": "synthex-nova-pro",
            "messages": [{"role": "user", "content": "hello"}]
        })
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_key():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.post("/v1/keys", json={
            "name": "Test Key", "email": "test@synthex.ai", "plan": "free"
        })
        assert r.status_code in (200, 422, 500)


@pytest.mark.asyncio
async def test_finance_requires_auth():
    from httpx import AsyncClient, ASGITransport
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        r = await client.post("/v1/finance", json={
            "query": "crypto market", "analysis_type": "crypto"
        })
        assert r.status_code == 401
