
class ContentModerationSystem:
    
    def __init__(self):
        self.filters = {
            "toxicity": ToxicityFilter(),
            "pii": PIIFilter(),
            "prohibited": ProhibitedContentFilter(),
            "custom": CustomBusinessFilter()
        }
        self.openai_mod = OpenAIModerationAPI()


    async def check_content(self, text, context=None):
        """Multi-layer content checking"""
        results = {
            "safe": True,
            "issues": [],
            "severity": "none"
        }
         # Layer 1: OpenAI moderation API
        openai_result = await self.openai_mod.check(text)
        if openai_result.flagged:
            results["safe"] = False
            results["issues"].append({
                "type": "openai_moderation",
                "categories": openai_result.categories,
                "severity": "high"
            })
         # Layer 2: Custom filters
        for name, filter in self.filters.items():
            filter_result = filter.check(text, context)
            if not filter_result.safe:
                results["safe"] = False
                results["issues"].append({
                    "type": name,
                    "details": filter_result.details,
                    "severity": filter_result.severity
                })
         # Determine overall severity
        if results["issues"]:
            severities = [issue["severity"] for issue in results["issues"]]
            results["severity"] = max(severities, key=["low", "medium", "high"].index)

        return results

    
    def get_safe_alternative(self, unsafe_content, issues):
        """Generate safe alternative responses"""
        if any(issue["type"] == "toxicity" for issue in issues):
            return "I'll help you with that in a more constructive way..."
        
        elif any(issue["type"] == "pii" for issue in issues):
            return "I've noticed some personal information. Let me help without using that..."
        
        else:
            return "I can't provide that specific content, but I can help with..."