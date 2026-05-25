from .analytics import router as analytics_router
from .content import router as content_router
from .smi import router as smi_router
from .market_research import router as market_research_router
from .dot_analysis import router as dot_analysis_router
from .help_colleague import router as help_colleague_router
from .trends import router as trends_router

__all__ = [
    "analytics_router",
    "content_router",
    "smi_router",
    "market_research_router",
    "dot_analysis_router",
    "help_colleague_router",
    "trends_router"
]
