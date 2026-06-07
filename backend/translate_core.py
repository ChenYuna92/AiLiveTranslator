import os
from typing import Optional

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import models, tmt_client

from utils.logger import get_logger


class Translator:
    def __init__(self, region: str = "ap-shanghai", source_lang: str = "en", target_lang: str = "zh"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.logger = get_logger("\u7ffb\u8bd1")
        self.cache: dict[str, str] = {}
        secret_id = os.getenv("TENCENT_SECRET_ID", "")
        secret_key = os.getenv("TENCENT_SECRET_KEY", "")
        self.client: Optional[tmt_client.TmtClient] = None
        if secret_id and secret_key:
            cred = credential.Credential(secret_id, secret_key)
            http_profile = HttpProfile()
            http_profile.endpoint = "tmt.tencentcloudapi.com"
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            self.client = tmt_client.TmtClient(cred, region, client_profile)

    def translate(self, text: str) -> str:
        if not text:
            return ""
        if text in self.cache:
            return self.cache[text]
        if self.client is None:
            return f"\u672a\u914d\u7f6e\u7ffb\u8bd1\u5bc6\u94a5\uff1a{text}"
        try:
            req = models.TextTranslateRequest()
            req.SourceText = text
            req.Source = self.source_lang
            req.Target = self.target_lang
            req.ProjectId = 0
            translated = self.client.TextTranslate(req).TargetText.strip()
            self.cache[text] = translated
            if len(self.cache) > 100:
                self.cache.pop(next(iter(self.cache)))
            return translated
        except Exception as exc:
            self.logger.error("\u7ffb\u8bd1\u5f02\u5e38: %s", exc)
            return f"\u7ffb\u8bd1\u5931\u8d25\uff1a{text}"
