from fastapi import APIRouter

from backend.api.schemas import (
    ModuleSchema,
    ModulesResponse,
    ModuleRunResponse,
    RunModuleRequest,
    module_run_to_response,
)
from backend.core.module_registry import module_registry
from backend.services.module_runner import module_runner

router = APIRouter(prefix="/api", tags=["modules"])


@router.get("/modules", response_model=ModulesResponse)
def list_modules() -> ModulesResponse:
    modules = [
        ModuleSchema(
            id=module.config.id,
            name=module.config.name,
            version=module.config.version,
            description=module.config.description,
            primary_lens=module.config.primary_lens,
            analytical_level=module.config.analytical_level.value,
            unit_of_analysis=module.config.unit_of_analysis,
            primary_question=module.config.primary_question,
            confidence_ceiling=module.config.confidence_ceiling.value,
            output_schema=module.config.output_schema,
            enabled=module.config.enabled,
            input_type=module.config.input_type,
            recommended_companions=module.config.recommended_companions,
        )
        for module in module_registry.list_modules()
    ]
    return ModulesResponse(modules=modules)


@router.post("/modules/{module_id}/run", response_model=ModuleRunResponse)
def run_module(module_id: str, request: RunModuleRequest) -> ModuleRunResponse:
    run = module_runner.run(
        module_id=module_id,
        transcript_id=request.transcript_id,
        model=request.model,
    )
    return module_run_to_response(run)


@router.get("/module-runs/{run_id}", response_model=ModuleRunResponse)
def get_module_run(run_id: str) -> ModuleRunResponse:
    run = module_runner.get(run_id)
    return module_run_to_response(run)
