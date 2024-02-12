export function ensureStorageSchema(gen: number) {
    console.log("Storage schema generation:", localStorage.gen)
    localStorage.gen ||= gen;
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
export function __loadTabID(): number {
    let _tabID: number = -1;
    // Duplicated Tabs will have the same tabID and peerID as their parent Tab; we must force reset those values
    if (!sessionStorage.tabID || isTabDuplicate || getTabState("lock", sessionStorage.tabID) != "") {
        console.warn("tab is duplicate", !sessionStorage.tabID, isTabDuplicate, sessionStorage.tabID ? getTabState("lock", sessionStorage.tabID) : "")
        _tabID = selectTabID();
    } else {
        _tabID = parseInt(sessionStorage.tabID);
    }
    setTabState("lock", "locked", _tabID);
    sessionStorage.tabID = _tabID;

    return _tabID;
}


export const tabID = __loadTabID()
console.warn("tabID", tabID)
addEventListener('beforeunload', function () {
    deleteTabState("lock", tabID);
});

function selectTabID() {
    for (let i = 1; i <= 1000; i++) {
        if (getTabState("lock", i) == "") {
            return i;
        }
    }
}

export function getTabState(key: string, _tabID: number = tabID): string {
    return localStorage[`tabState:${_tabID}:${key}`] || "";
}

export function deleteTabState(key: string, _tabID: number = tabID) {
    delete localStorage[`tabState:${_tabID}:${key}`];
}

export function setTabState(key: string, value: string, _tabID: number = tabID) {
    localStorage[`tabState:${_tabID}:${key}`] = value;
}
