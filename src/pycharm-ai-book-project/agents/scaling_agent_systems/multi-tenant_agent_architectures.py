from asyncio.log import logger
from typing import Any
from collections.abc import Mapping

import hashlib
import time

from anthropic import RateLimitError, AnthropicError


class MultiTenantAgentManager:

    def __init__(self, base_config: Mapping[str, Any]):
        self.base_config = base_config
        self.tenant_agents = {}
        self.tenant_configs = {}
        self.resource_limits = {}


    def create_tenant_agent(self, 
                           tenant_id: str, 
                           custom_config: Mapping[str, Any]) -> str:
        """Create isolated agent instance for tenant"""
        # Merge configurations
        tenant_config = {**self.base_config, **custom_config}
         # Set resource limits
        self.resource_limits[tenant_id] = {
            "max_daily_tokens": custom_config.get("max_daily_tokens", 100000),
            "max_concurrent_requests": custom_config.get("max_concurrent_requests", 10),
            "max_monthly_cost": custom_config.get("max_monthly_cost", 1000),
            "allowed_tools": custom_config.get("allowed_tools", ["search", "calculate"])
        }
         # Create isolated agent
        agent = self.build_agent(tenant_config, tenant_id)
         # Store references
        agent_id = hashlib.sha256(f"{tenant_id}:{time.time()}".encode()).hexdigest()[:12]
        self.tenant_agents[agent_id] = agent
        self.tenant_configs[agent_id] = tenant_config

        logger.info(
            "tenant_agent_created",
            tenant_id=tenant_id,
            agent_id=agent_id,
            config=tenant_config
        )
        
        return agent_id

    
    def build_agent(self, 
                   config: Mapping[str, Any], 
                   tenant_id: str) -> Any:
        """Build agent with tenant-specific configuration"""
        # Create custom prompt template
        system_prompt = f"""
        You are an AI assistant for {config.get('company_name', 'the organization')}.
        Guidelines:
           - {config.get('tone', 'Be professional and helpful')}
           - {config.get('restrictions', 'Follow all company policies')}
           - Your responses should align with these values: {config.get('values', [])}
        Available tools: {config.get('tools', [])}
        """
        # Initialize agent with tenant-specific components
        llm = self.create_llm(config)
        tools = self.create_tools(config, tenant_id)
        memory = self.create_memory(tenant_id)
        agent = self.create_react_agent(
                llm=llm,
                tools=tools,
                prompt=system_prompt,
                memory=memory
        )
        # Wrap with tenant-specific middleware

        return TenantAwareAgent(agent, tenant_id, self.resource_limits[tenant_id])

    
class TenantAwareAgent:

    def __init__(self, base_agent, tenant_id: str, limits: Mapping[str, Any]):
        self.agent = base_agent
        self.tenant_id = tenant_id
        self.limits = limits
        self.usage_tracker = TenantUsageTracker(tenant_id)

    async def run(self, task: str, **kwargs) -> str:
        """Execute task with tenant isolation and limits"""
        
        # Check rate limits
        if not await self.usage_tracker.check_rate_limit(
            self.limits["max_concurrent_requests"]
        ):
            raise RateLimitError(
                f"Tenant {self.tenant_id} exceeded concurrent request limit"
            )
        
         # Check token limits
        estimated_tokens = len(task.split()) * 2  # Rough estimate
        if not await self.usage_tracker.check_token_limit(
            estimated_tokens,
            self.limits["max_daily_tokens"]
        ):
            raise AnthropicError (
                    f"Tenant {self.tenant_id} exceeded daily token limit"
            )
             # Execute with isolation
        try:
            result = await self.agent.arun(task, **kwargs)
            # Track usage
            await self.usage_tracker.record_usage(
                tokens=estimated_tokens,
                cost=self.estimate_cost(estimated_tokens)
            )

            return result
        
        except Exception as e:
            logger.error(
                "tenant_agent_error",
                tenant_id=self.tenant_id,
                error=str(e),
                task=task
            )

            raise


class TenantUsageTracker:
    
    pass