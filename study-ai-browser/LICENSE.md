# Study AI Browser licensing

## Chromium engine — BSD 3-Clause

The browser engine distributed in the APK is Chromium, Copyright (c) The
Chromium Authors. It is used under the BSD 3-Clause license. The pinned
Chromium checkout ships Chromium's `LICENSE` file, and the built APK embeds
the licenses generated from the checkout by Chromium's build
(`about_credits.html` / system WebView license resources), which cover
Chromium and all of its bundled third-party components.

The Chromium license text (as pinned in the checkout's `LICENSE` file) applies
to everything produced from the Chromium sources:

> Copyright 2015 The Chromium Authors
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:
>
> 1. Redistributions of source code must retain the above copyright notice,
>    this list of conditions and the following disclaimer.
> 2. Redistributions in binary form must reproduce the above copyright notice,
>    this list of conditions and the following disclaimer in the documentation
>    and/or other materials provided with the distribution.
> 3. Neither the name of the copyright holder nor the names of its contributors
>    may be used to endorse or promote products derived from this software
>    without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
> AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
> IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
> ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
> LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
> CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
> SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
> INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
> CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
> ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
> POSSIBILITY OF SUCH DAMAGE.

Copyright notices and the license references inside the Chromium tree are
preserved: the patch engine is forbidden from modifying license files
(review-enforced; patches touch only the files listed in `patches/`).

## Study AI Browser additions — Apache 2.0

This repository's original content (project configuration, patches, scripts,
tests, documentation, branding assets in `branding/`, and the Java sources in
`src-custom/`) is Copyright 2026 Study AI Browser contributors and licensed
under the Apache License, Version 2.0. A copy of the license text is available
at https://www.apache.org/licenses/LICENSE-2.0.
