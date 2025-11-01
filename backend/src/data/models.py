from enum import StrEnum


class ModelTask(StrEnum):
    SUPERVISE = 'supervise'
    DATA_ANALYSIS = 'analyze_data'
    DATA_TREATMENT = 'data_treat'
    REPORT_GENERATION = 'report_gen'
    INVOICE_VALIDATION = 'validate_taxes'
    DEFAULT = 'default'


MODELS = {
    'qwen/qwen3-32b': 'groq',
    'llama-3.1-8b-instant': 'groq',
    'llama-3.3-70b-versatile': 'groq',
    'meta-llama/llama-4-maverick-17b-128e-instruct': 'groq',
    'meta-llama/llama-4-scout-17b-16e-instruct': 'groq',
    'openai/gpt-oss-20b': 'groq',
    'openai/gpt-oss-120b': 'groq',
    'gemini-2.5-flash': 'google',
    'gemini-2.5-pro': 'google',
}


TASK_PREDEFINED_MODELS = {
    'groq': {
        ModelTask.SUPERVISE: 'qwen/qwen3-32b',
        ModelTask.DATA_ANALYSIS: 'meta-llama/llama-4-maverick-17b-128e-instruct',
        ModelTask.DATA_TREATMENT: 'llama-3.3-70b-versatile',
        ModelTask.REPORT_GENERATION: 'openai/gpt-oss-120b',
        ModelTask.INVOICE_VALIDATION: 'openai/gpt-oss-120b',
        ModelTask.DEFAULT: 'llama-3.1-8b-instant',
    },
    'google': {
        ModelTask.SUPERVISE: 'gemini-2.5-flash',
        ModelTask.DATA_ANALYSIS: 'gemini-2.5-pro',
        ModelTask.DATA_TREATMENT: 'gemini-2.5-flash',
        ModelTask.REPORT_GENERATION: 'gemini-2.5-flash',
        ModelTask.INVOICE_VALIDATION: 'gemini-2.5-pro',
        ModelTask.DEFAULT: 'gemini-2.5-flash',
    },
}
