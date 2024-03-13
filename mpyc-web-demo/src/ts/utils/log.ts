

export const tableLogger = (selector = "#output", columns = ["Data"]) => (...data: any[]) => {
    const table = ensureLogTable(selector, columns)


    const row = table.insertRow()
    for (let arg of data) {

        const cell = row.insertCell()
        cell.textContent = arg
        cell.style.paddingRight = "50px"
    }
}

export const ensureLogTable = (selector = "#output", columns = ["Data"]) => {
    const div = document.querySelector<HTMLDivElement>(selector)!
    let existingTable = div.querySelector<HTMLTableElement>("table")
    if (existingTable) {
        return existingTable;
    }

    const newTable = document.createElement("table")
    const headRow = newTable.createTHead().insertRow()
    headRow.style.borderBottom = "1px solid #ccc"
    for (let column of columns) {
        headRow.insertCell().textContent = column
    }
    div.insertAdjacentElement("beforeend", newTable)
    return newTable
}

export const logTable = tableLogger("#output")

