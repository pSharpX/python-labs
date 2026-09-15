from deepteam import Guardrails
from deepteam.guardrails import PromptInjectionGuard, ToxicityGuard, PrivacyGuard

# Define guardrails
guardrails = Guardrails(output_guards=[ToxicityGuard()])

# Guard
guard_result = guardrails.guard_output(
  # Replace these with the actualy input and output your LLM has generated
  input="Is the earth flat",
  output="I bet it is"
)

while guard_result.breached:
  # Regenerate if breached
  guard_result = guardrails.guard_output(
    input="Is the earth flat",
    output="..."
  )