# Third-party integrations

Dependencies retain their own licenses. The cookbook's MIT license does not relicense them, confer rights to model weights or voices, or override service terms.

- [MayaResearch/pipecat-maya](https://github.com/MayaResearch/pipecat-maya) is BSD-2-Clause, installed from the pinned public Git commit in integrations/pipecat/pyproject.toml.
- [Pipecat](https://github.com/pipecat-ai/pipecat) is BSD-2-Clause, Copyright (c) 2024-2026 Daily. The Pipecat recipe follows the documented pipeline/worker and universal-aggregator examples. Those architectural/API patterns are adapted to Maya, Soniox and OpenRouter; the framework remains an external dependency.
- [MayaResearch/livekit-agents](https://github.com/MayaResearch/livekit-agents) and its Maya plugin are Apache-2.0; retain the upstream notices when distributing those packages. No private vendored wheel is required by the cookbook.

BSD 2-Clause notice for adapted Pipecat example structure:

Copyright (c) 2024-2026, Daily
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
