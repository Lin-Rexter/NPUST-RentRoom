/* = = = 搜尋框 = = = */
var tenant_search = document.getElementById("tenant_search");
var review_search = document.getElementById("review_search");
var report_search = document.getElementById("report_search");
var feedback_search = document.getElementById("feedback_search");
var block_search = document.getElementById("block_search");

/* = = = 表單資料 = = =*/
var tenant_body = document.getElementById("tenant_body");
var review_body = document.getElementById("review_body");
var report_body = document.getElementById("report_body");
var feedback_body = document.getElementById("feedback_body");
var block_body = document.getElementById("block_body");


/* 租客資料搜尋 */
tenant_search.addEventListener('input', () => {
    tenant_body.deleteRow(0)
    tenant_body.insertRow(0)
    tenant_body.insertCell(0)
})

/* 評論資料搜尋 */
review_search.addEventListener('input', () => {

})

/* 檢舉資料搜尋 */
report_search.addEventListener('input', () => {

})

/* 回報資料搜尋 */
feedback_search.addEventListener('input', () => {

})

/* 黑名單資料搜尋 */
block_search.addEventListener('input', () => {

})

/* 刪除所在的Row */
function deleteRow(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

/* 將所在的Row轉為可編輯狀態 */
is_edit = false;
function editRow(btn) {
    var row = btn.parentNode.parentNode;
    var td = row.getElementsByTagName('td');

    if (!is_edit) {
        // 將Row的每個資料轉成可編輯狀態
        for (i = 0; i < td.length - 1; i++) {
            td[i].style.border = "3px solid red";
            td[i].style.color = "white";
            td[i].style.background = "rgb(50, 50, 50)";
            td[i].setAttribute('contenteditable', true)
        }

        btn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> 完成'
        btn.classList.remove("btn-warning")
        btn.classList.add("btn-success", "border", "border-3", "border-light")
    } else {
        // 將Row的每個資料禁用可編輯狀態
        for (i = 0; i < td.length - 1; i++) {
            td[i].style.border = "";
            td[i].style.color = "";
            td[i].style.background = "";
            td[i].setAttribute('contenteditable', false)
        }

        btn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> 編輯'
        btn.classList.remove("btn-success", "border", "border-3", "border-light")
        btn.classList.add("btn-warning")
    }

    is_edit = !is_edit;
}
