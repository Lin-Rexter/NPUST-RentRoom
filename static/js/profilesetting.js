let isEditing = false; // 紀錄編輯狀態
let isPhoneValidated = false; // 記錄電話號碼是否已通過驗證
let phoneInput = document.getElementById('phone'); // 電話欄位
let avatarFile = document.getElementById('avatar-input'); // 大頭貼圖片上傳欄位
let avatarImage = document.getElementById('avatar-image'); // 大頭貼圖片
let originalAvatarSrc = avatarImage.src; // 新增，用來儲存初始圖片來源
let inputs = document.getElementsByClassName('form-control'); // 輸入框
let editButton = document.getElementById('edit-button'); // 編輯按鈕
let cancelButton = document.getElementById('cancel-button'); // 取消按鈕
let validateButton = document.getElementById('validate-button'); // 驗證按鈕
let fileUploadButton = document.getElementById('file-upload-button'); // 附加檔案上傳按鈕
let attach_info = document.getElementById('file-name'); // 附加檔案資訊欄
let submit_button = document.getElementById('submit-button'); // 提交按鈕
var attach_sizes = [];


// 圖片上傳
avatarFile.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            avatarImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// 當完成電話輸入時
phoneInput.addEventListener('change', () => {
    validateButton.style.display = ''; // 顯示驗證按鈕
    editButton.setAttribute('readonly', ''); // 禁用 "儲存" 按鈕
});

// 驗證電話號碼格式
function validatePhone() {
    // 是否為10位數字
    let regex = /^\d{10}$/;

    // 判斷是否符合格式
    if (!regex.test(phoneInput.value)) {
        // 彈出提示框
        show_toast("電話號碼格式不正確！", 'warning');
        return false;
    }

    show_toast("電話號碼格式正確！", 'tip');
    validateButton.style.display = 'none'; // 驗證成功後隱藏驗證按鈕
    editButton.removeAttribute('readonly'); // 驗證成功後啟用 "確認編輯" 按鈕
    isPhoneValidated = true; // 設定電話號碼已通過驗證
    return true;
}

// 按下編輯按鈕動作
function toggleEditing(e) {
    if (isEditing) { // 第二次按下儲存(編輯)按鈕時
        // 驗證上傳的檔案總大小(限制最大50MB)
        if (attach_sizes.length) {
            // 檔按總大小
            let attach_total_size = get_file_size(attach_sizes.reduce((sum, size) => sum + size), 2);
            if ((attach_total_size / 1024) > 50) {
                show_toast("檔案總大小超過50MB限制", 'warning');
                e.stopPropagation();
            }
        }

        // 禁用全部輸入框
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('readonly', '');
        }
        editButton.value = "編輯"; // 變更編輯按鈕文字
        cancelButton.style.display = 'none'; // 當完成編輯後，隱藏 "取消編輯" 按鈕
        fileUploadButton.style.display = 'none'; // 隱藏 "上傳附加檔案" 按鈕

        submit_button.style.display = "" // 顯示提交按紐
    } else { // 初次按下編輯按鈕時
        // 啟用全部輸入框
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].removeAttribute('readonly');
        }
        editButton.value = "儲存"; // 變更編輯按鈕文字
        cancelButton.style.display = ''; // 當開始編輯後，顯示 "取消編輯" 按鈕
        fileUploadButton.style.display = ''; // 顯示 "上傳附加檔案" 按鈕
    }
    // 更改編輯狀態
    isEditing = !isEditing;
}

// 按下取消編輯按鈕動作
function cancelEditing() {
    cancelButton.style.display = "none"; // 隱藏取消按鈕
    validateButton.style.display = 'none'; // 隱藏驗證按鈕
    fileUploadButton.style.display = 'none'; // 隱藏 "上傳附加檔案" 按鈕
    editButton.value = "編輯"; // 還原編輯按鈕文字
    editButton.removeAttribute('readonly'); // 啟用 "編輯" 按鈕

    for (let i = 0; i < inputs.length; i++) {
        inputs[i].setAttribute('readonly', ''); // 禁用全部輸入框
        inputs[i].value = inputs[i].defaultValue; // 將所有輸入框還原為預設值
    }

    avatarImage.src = originalAvatarSrc; // 還原初始大頭貼圖片

    isPhoneValidated = true; // 設定電話號碼已通過驗證
    isEditing = false; // 關閉編輯狀態
}

// 按下上傳檔案按鈕動作
fileUploadButton.addEventListener('change', function () {
    //avatarFile.click();
    let files = this.files

    // 判斷是否有上傳檔案，並將檔案資訊更新至欄位
    if (!files.length) {
        attach_info.value = "未上傳任何檔案"
    } else {
        // 清除檔案資訊欄
        attach_info.value = "";

        // 印出所有上傳的檔案資訊(檔名、檔案大小KB)
        Object.entries(files).forEach(file => {
            const [key, value] = file;
            const name = value.name,
                size = value.size;

            attach_sizes.push(size); // 儲存上傳的檔案大小

            attach_info.value += `${Number(key) + 1}.${name}(${get_file_size(size, 2)} KB)`;
            if (key < files.length - 1) {
                attach_info.value += "，";
            }
        });
    }
});

// 轉換檔案大小至 KB
// decimal: 取至小數點位置
function get_file_size(Bytes, decimal) {
    let exponent = Math.pow(10, decimal);
    return Math.round(((Bytes / 1024) * exponent)) / exponent;
}