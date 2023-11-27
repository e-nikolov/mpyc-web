export function ensureStorageSchema(gen: number) {
    console.log("Storage schema generation:", localStorage.gen)
    localStorage.gen ||= 0;
    if (localStorage.gen < gen) {
        console.log(`Clearing schema, latest generation: ${gen}`)
        localStorage.clear();
        sessionStorage.clear();
        localStorage.gen = gen;
    }
}

const __isTabDuplicate = () => {
    // return window.performance.getEntriesByType("navigation")[0].type == 'back_forward'
    addEventListener('beforeunload', function () {
        delete sessionStorage.__lock;
    });
    let dup = false;
    if (sessionStorage.__lock) {
        dup = true;
    }
    sessionStorage.__lock = 1;
    return dup
}
export const isTabDuplicate = __isTabDuplicate()


// TODO: not thread safe, breaks if tabs open too quickly
export function loadPeerID(): string {
    localStorage.tabCount ||= 0;
    let tabCount = parseInt(localStorage.tabCount) + 1;
    localStorage.tabCount = tabCount;

    addEventListener('beforeunload', function () {
        setTabState("lock", "");
        let tabCount = parseInt(localStorage.tabCount);
        if (tabCount > 0) {
            localStorage.tabCount = tabCount - 1;
        }
    });

    if (isTabDuplicate) {
        console.warn("tab is duplicate")
    }

    // Duplicated Tabs will have the same tabID and peerID as their parent Tab; we must force reset those values
    if (!sessionStorage.tabID || isTabDuplicate || getTabState("lock", sessionStorage.tabID) != "") {
        sessionStorage.tabID = selectTabID();
        sessionStorage.myPeerID = getTabState("myPeerID");
    }

    setTabState("lock", "locked");

    console.log("tab id: " + sessionStorage.tabID);
    return sessionStorage.myPeerID;
}

function selectTabID() {
    for (let i = 1; i <= 1000; i++) {
        if (getTabState("lock", i) == "") {
            return i;
        }
    }
}

export function getTabState(key: string, tabID = sessionStorage.tabID) {
    return localStorage[`tabState:${tabID}:` + key] || "";
}

export function setTabState(key: string, value: any, tabID = sessionStorage.tabID) {
    sessionStorage[key] = value;
    localStorage[`tabState:${tabID}:` + key] = value;
}
