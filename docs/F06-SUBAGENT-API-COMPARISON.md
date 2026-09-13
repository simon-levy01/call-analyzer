# Subagent versus API pilot — 13 September 2026

Two actual Codex subagents were configured through spawn_agent: gpt-5.6-luna / low and gpt-5.6-terra / low, each with fork_turns=none. Each answered three saved synthetic API inputs without access to baseline answers. No new external inference API calls were made. Incremental API cost: $0; Codex subscription usage applies and was not metered per subagent here.

## Method and limits

The inputs and instructions are exact historical frozen checkpoints from the previous Luna/Terra comparison: stress_only_then_rent/4/6, vague_job_user_script/4/14, prize/4/16. Existing outputs from both API models were reused. Agents received the current GuidanceOutput JSON schema and the original output token limit as text. They wrote JSON files; the token limit and API structured-output decoding were not enforced by the agent runtime. Ordinary application schema validation was then applied.

The requested model and low reasoning settings were accepted by the orchestration tool. This does not verify identical backend snapshots or sampling settings. Agent system/developer instructions, tool context and output generation differ from the Responses API. Three cases shared each agent session, so they were not isolated API requests. No live timing, retrieval, post-call generation, rate limits, API cost behavior or production UI was tested. This is a small exploratory comparison, not evidence of statistical equivalence.

## Results

| Case | Luna API / agent | Terra API / agent |
|---|---|---|
| Generic stress | Both correctly omit distracting memories | Both correctly omit distracting memories |
| Rent trouble | Both select the possible McDonald's job-loss connection | Both select the possible McDonald's job-loss connection |
| Unnamed prize | Both select the photography-prize memory | Both select the photography-prize memory |

All six agent outputs parse with the application's Pydantic schema. All referenced memory IDs are supplied IDs. Memory selection matches the corresponding historical API output in 6/6 pairs. This is decision agreement, not overall accuracy or identical wording. Terra omitted optional fields that the application supplies by default; this does not demonstrate strict API schema compliance.

Manual differences:

- Luna agent asks “What was the photo that won?” although the current contact never established the competition was photography. Its explanation says the memory helps identify the event; the API output instead asks what the winning entry was. The agent's reminder still says “Possibly related,” but the follow-up loses that restraint.
- Luna agent raises the rent and prize reminder confidence from the API's medium to high. It also retains the API's overly strong high-confidence inferred positive tone in the prize case. The API's “must feel incredible” reply was itself an unsupported emotional assumption, so the baseline is not a perfect answer.
- Terra agent removes “Possibly related:” from the prize reminder and assigns high confidence, whereas its API result keeps the tentative link and medium confidence.
- Terra agent labels “I still cannot believe it” as high-confidence uncertainty. In this context it reads as celebratory disbelief; the API's medium-confidence positive/excited interpretation is better supported.
- Generic stress and rent support remain broadly useful in both delivery methods. Wording, alternatives and follow-up choices vary.

## Use

Subagents are useful for subscription-funded preliminary prompt checks and generating candidate responses for review. They cannot establish the app's real API performance. Keep a small real-API acceptance run for final prompt changes, especially uncertain references, evidence calibration, structured output and latency. This pilot does not establish that the app can use Codex subscription access as an API replacement.

Raw cases, baselines, outputs and validation are in `build/subagent-model-comparison-20260913/`. Run `.venv/Scripts/python.exe -X utf8 build/subagent-model-comparison-20260913/check.py` for the offline checks. Production settings are unchanged.
