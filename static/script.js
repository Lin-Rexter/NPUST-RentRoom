var black_list = document.getElementsByClassName("block_list")[0];

// 隨機範圍數字
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 隨機特定長度名字
function getRandomName(length) {
    let result = "";
    const characters =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(
            Math.floor(Math.random() * charactersLength)
        );
        counter += 1;
    }
    return result;
}

var options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric"
};

// 隨機日期
function getRandomDate(start, end) {
    return new Date(
        start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
}

// 新增IP
function add_ip(id, ip, name, date, status) {
    black_list.innerHTML += `
        <tr class="ip">
          <td data-th="ID">${id}</td>
          <td data-th="IP位置">${ip}</td>
          <td data-th="使用者ID">@${name}</td>
          <td data-th="新增日期">${date}</td>
          <td data-th="狀態">${status}</td>
          <td data-th="功能">
            <button
              class="nav-link fw-bold text-white btn btn-danger remove_ip"
              type="button"
              id="remove"
            >
              <i class="fa-solid fa-trash"></i>
              移除
            </button>
          </td>
        </tr>`;
}

var Status = ["停權中", "二次停權中", "永久停權中"]
function add_many_ip(total) {
    for (var i = 0; i < total; i++) {
        add_ip(
            i + 1,
            `${getRandomInt(1, 255)}.${getRandomInt(0, 255)}.${getRandomInt(
                0,
                255
            )}.${getRandomInt(0, 255)}`,
            `${getRandomName(getRandomInt(10, 10))}`,
            getRandomDate(new Date(2022, 0, 1), new Date()).toLocaleDateString(
                "zh-TW",
                options
            ),
            Status[getRandomInt(0, Status.length-1)]
        );
    }
}

add_many_ip(20);

// 移除IP列按鈕
const deleteButtons = document.querySelectorAll("#remove");

const ip_tr = document.getElementsByClassName(".ip");

// 循環相同id按鈕，偵測到所點擊的按鈕進行移除
deleteButtons.forEach((button) => {
    button.addEventListener("click", remove_ip);
});

// 移除功能
function remove_ip() {
    this.closest("tr").remove();
}

// 新增IP按鈕
/*
document.addEventListener("click", () => {
    if (black_list.getElementsByTagName("tr").length === 0) {
        black_list.innerHTML += `
          <tr id="add">
              <button
                class="nav-link fw-bold text-white btn btn-info"
                type="button"
                onclick="AddIp()"
              >
                <i class="fa-solid fa-trash"></i>
                新增
              </button>
          </tr>`;
    }
});

function AddIp() {
    add_many_ip(2);
}
*/