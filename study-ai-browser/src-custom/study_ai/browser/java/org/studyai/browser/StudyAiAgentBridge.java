// Copyright 2026 Study AI Browser contributors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package org.studyai.browser;

/**
 * Extension point reserved for a later Study AI phase (AI API and the
 * MCP-powered browser agent). This interface is pure plumbing:
 *
 * <ul>
 *   <li>Implementations must keep all browser data on the device.</li>
 *   <li>Implementations must never embed API keys or secrets; credentials,
 *       when needed, are supplied at runtime by the user or a backend the
 *       user explicitly connects.</li>
 *   <li>No implementation is registered today; the browser's behaviour is
 *       unchanged until a later phase ships one.</li>
 * </ul>
 */
public interface StudyAiAgentBridge {
    /** Stable identifier of the bridge, e.g. "studyai.agent". */
    String id();

    /**
     * Handle a command issued to this bridge.
     *
     * @param command     dot-separated command name, e.g. "page.summarize"
     * @param payloadJson UTF-8 JSON payload, or null when absent
     * @return true when the command was consumed, false to allow other
     *         registered bridges to handle it
     */
    boolean onCommand(String command, String payloadJson);
}
