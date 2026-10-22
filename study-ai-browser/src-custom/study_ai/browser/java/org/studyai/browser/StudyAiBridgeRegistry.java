// Copyright 2026 Study AI Browser contributors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package org.studyai.browser;

import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * Registry and dispatcher for {@link StudyAiAgentBridge} implementations.
 * Thread-safe; empty by default, so the browser behaves exactly like stock
 * Chromium until a later Study AI phase registers a bridge.
 */
public final class StudyAiBridgeRegistry {
    private static final Set<StudyAiAgentBridge> BRIDGES =
            Collections.synchronizedSet(new LinkedHashSet<>());

    private StudyAiBridgeRegistry() {}

    public static void register(StudyAiAgentBridge bridge) {
        if (bridge != null) {
            BRIDGES.add(bridge);
        }
    }

    public static void unregister(StudyAiAgentBridge bridge) {
        if (bridge != null) {
            BRIDGES.remove(bridge);
        }
    }

    public static Set<StudyAiAgentBridge> bridges() {
        return Collections.unmodifiableSet(BRIDGES);
    }

    /**
     * Dispatch a command to the registered bridges in registration order.
     *
     * @return true when some bridge consumed the command
     */
    public static boolean dispatch(String command, String payloadJson) {
        for (StudyAiAgentBridge bridge : bridges()) {
            if (bridge.onCommand(command, payloadJson)) {
                return true;
            }
        }
        return false;
    }
}
