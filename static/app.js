/**
 * 案源價值論述生成系統 — 前端互動邏輯
 */

(() => {
  'use strict';

  // ── DOM 元素 ──
  const formSection = document.getElementById('form-section');
  const progressSection = document.getElementById('progress-section');
  const errorSection = document.getElementById('error-section');
  const resultSection = document.getElementById('result-section');

  const form = document.getElementById('generate-form');
  const btnSubmit = document.getElementById('btn-submit');
  const btnRetry = document.getElementById('btn-retry');
  const btnNew = document.getElementById('btn-new');
  const btnDownloadMd = document.getElementById('btn-download-md');
  const btnDownloadPptx = document.getElementById('btn-download-pptx');
  const btnCopyMd = document.getElementById('btn-copy-md');

  const progressBar = document.getElementById('progress-bar');
  const progressStep = document.getElementById('progress-step');
  const progressPct = document.getElementById('progress-pct');
  const progressStatus = document.getElementById('progress-status');
  const stepDetails = document.getElementById('step-details');
  const errorMessage = document.getElementById('error-message');
  const warningsBlock = document.getElementById('warnings-block');
  const warningsList = document.getElementById('warnings-list');
  const markdownPreview = document.getElementById('markdown-preview');

  let currentTaskId = null;
  let pollTimer = null;
  let rawMarkdown = '';

  // ── 工具函式 ──
  function showSection(section) {
    [formSection, progressSection, errorSection, resultSection].forEach(s => {
      s.classList.add('hidden');
    });
    section.classList.remove('hidden');
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function showToast(message) {
    let toast = document.querySelector('.toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }

  function updateStepUI(currentStep) {
    const items = stepDetails.querySelectorAll('.step-item');
    items.forEach(item => {
      const step = parseInt(item.getAttribute('data-step'));
      item.classList.remove('active', 'done');
      if (step < currentStep) {
        item.classList.add('done');
      } else if (step === currentStep) {
        item.classList.add('active');
      }
    });
  }

  // ── Step 0 顧問觀點收合 ──
  const expertToggle = document.getElementById('expert-toggle');
  const expertPanel = document.getElementById('expert-panel');
  const expertChevron = document.getElementById('expert-chevron');

  if (expertToggle) {
    expertToggle.addEventListener('click', () => {
      const isOpen = !expertPanel.classList.contains('hidden');
      expertPanel.classList.toggle('hidden', isOpen);
      expertChevron.style.transform = isOpen ? '' : 'rotate(180deg)';
    });
  }

  // ── 表單提交 ──
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const expertInput = {
      core_argument: (document.getElementById('expert_core_argument')?.value || '').trim(),
      iii_angle: (document.getElementById('expert_iii_angle')?.value || '').trim(),
      concern: (document.getElementById('expert_concern')?.value || '').trim(),
    };

    const data = {
      company_name: document.getElementById('company_name').value.trim(),
      industry: document.getElementById('industry').value,
      transformation_topic: document.getElementById('transformation_topic').value.trim(),
      supplement: document.getElementById('supplement').value.trim(),
      expert_input: expertInput,
    };

    if (!data.company_name || !data.industry || !data.transformation_topic) {
      showToast('請填寫所有必填欄位');
      return;
    }

    btnSubmit.disabled = true;
    btnSubmit.textContent = '⏳ 提交中...';

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (!res.ok) {
        throw new Error(result.error || '提交失敗');
      }

      currentTaskId = result.task_id;

      // 切換到進度畫面
      showSection(progressSection);

      // 重置進度 UI
      progressBar.style.width = '0%';
      progressPct.textContent = '0%';
      progressStep.textContent = '步驟 0/6';
      progressStatus.textContent = '正在準備...';
      updateStepUI(0);

      // 開始輪詢
      startPolling();

    } catch (err) {
      showToast(err.message);
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.textContent = '🚀 開始生成';
    }
  });

  // ── 進度輪詢 ──
  function startPolling() {
    if (pollTimer) clearInterval(pollTimer);

    pollTimer = setInterval(async () => {
      if (!currentTaskId) return;

      try {
        const res = await fetch(`/api/status/${currentTaskId}`);
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.error || '查詢失敗');
        }

        // 更新進度
        progressBar.style.width = data.progress + '%';
        progressPct.textContent = data.progress + '%';
        progressStep.textContent = `步驟 ${data.step}/6`;
        progressStatus.textContent = data.step_name || '處理中...';
        updateStepUI(data.step);

        // 完成
        if (data.status === 'done') {
          clearInterval(pollTimer);
          pollTimer = null;

          // 載入結果
          await loadResult();

          // 顯示警告
          if (data.warnings && data.warnings.length > 0) {
            warningsBlock.classList.remove('hidden');
            warningsList.innerHTML = data.warnings
              .map(w => `<li>⚠️ ${w}</li>`)
              .join('');
          } else {
            warningsBlock.classList.add('hidden');
          }

          // PPTX 按鈕狀態
          if (!data.pptx_ok) {
            btnDownloadPptx.disabled = true;
            btnDownloadPptx.textContent = '📊 PPTX 不可用';
            btnDownloadPptx.classList.add('opacity-50', 'cursor-not-allowed');
          } else {
            btnDownloadPptx.disabled = false;
            btnDownloadPptx.textContent = '📊 下載 PPTX';
            btnDownloadPptx.classList.remove('opacity-50', 'cursor-not-allowed');
          }

          showSection(resultSection);
        }

        // 錯誤
        if (data.status === 'error') {
          clearInterval(pollTimer);
          pollTimer = null;
          errorMessage.textContent = data.error || '未知錯誤，請重試。';
          showSection(errorSection);
        }

      } catch (err) {
        // 網路錯誤不停止輪詢，僅記錄
        console.error('Polling error:', err);
      }
    }, 2000); // 每 2 秒輪詢
  }

  // ── 載入結果 ──
  async function loadResult() {
    if (!currentTaskId) return;

    try {
      const res = await fetch(`/api/result/${currentTaskId}/markdown`);
      const data = await res.json();

      if (res.ok && data.content) {
        rawMarkdown = data.content;
        markdownPreview.innerHTML = marked.parse(data.content);
      }
    } catch (err) {
      console.error('Load result error:', err);
      markdownPreview.innerHTML = '<p class="text-red-400">無法載入預覽內容</p>';
    }
  }

  // ── 下載 Markdown（客戶端直接生成，不依賴伺服器暫存檔） ──
  btnDownloadMd.addEventListener('click', () => {
    if (!rawMarkdown) {
      showToast('沒有可下載的內容，請重新生成');
      return;
    }
    const blob = new Blob([rawMarkdown], { type: 'text/markdown; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const company = document.getElementById('company_name').value.trim() || '未命名';
    a.href = url;
    a.download = `${date}_${company}_案源價值說明.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('✅ Markdown 檔案下載中...');
  });

  // ── 下載 PPTX（透過 fetch 下載，加錯誤處理） ──
  btnDownloadPptx.addEventListener('click', async () => {
    if (!currentTaskId) return;
    try {
      const res = await fetch(`/api/result/${currentTaskId}/download/pptx`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || '下載失敗，請重新生成後再試');
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const company = document.getElementById('company_name').value.trim() || '未命名';
      a.href = url;
      a.download = `${date}_${company}_案源價值說明.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('✅ PPTX 簡報下載中...');
    } catch (err) {
      showToast('❌ ' + err.message);
    }
  });

  // ── 複製 Markdown ──
  btnCopyMd.addEventListener('click', async () => {
    if (!rawMarkdown) {
      showToast('沒有可複製的內容');
      return;
    }
    try {
      await navigator.clipboard.writeText(rawMarkdown);
      showToast('✅ 已複製到剪貼簿');
    } catch {
      showToast('複製失敗，請手動選取');
    }
  });

  // ── 重試 ──
  btnRetry.addEventListener('click', () => {
    showSection(formSection);
  });

  // ── 新增分析 ──
  btnNew.addEventListener('click', () => {
    form.reset();
    currentTaskId = null;
    rawMarkdown = '';
    showSection(formSection);
  });

})();
