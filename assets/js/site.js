(() => {
  "use strict";

  const results = window.TUTORIAL_RESULTS || {};
  const progressBar = document.querySelector("#reading-progress-bar");
  const menuButton = document.querySelector("#menu-button");
  const scrim = document.querySelector("#mobile-scrim");
  const navLinks = Array.from(document.querySelectorAll(".nav-link"));
  const sections = Array.from(document.querySelectorAll("section[id]"));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function readPath(object, path) {
    return path.split(".").reduce((value, key) => {
      if (value === undefined || value === null) return undefined;
      return value[key];
    }, object);
  }

  function formatValue(value, format) {
    if (value === undefined || value === null || Number.isNaN(Number(value))) {
      return "—";
    }
    if (format === "percent") {
      return `${(Number(value) * 100).toFixed(1)}%`;
    }
    if (format === "integer") {
      return new Intl.NumberFormat("en").format(Number(value));
    }
    if (format === "decimal") {
      return Number(value).toFixed(2);
    }
    return String(value);
  }

  document.querySelectorAll("[data-result]").forEach((element) => {
    const value = readPath(results, element.dataset.result);
    element.textContent = formatValue(value, element.dataset.format);
  });

  const artifactBoxes = Array.from(document.querySelectorAll("[data-artifact]"));
  const artifactCount = document.querySelector("#artifact-progress-count");
  const artifactStorageKey = "ds-workflow-artifacts-v1";

  function readArtifactState() {
    try {
      const stored = JSON.parse(localStorage.getItem(artifactStorageKey) || "{}");
      return stored && typeof stored === "object" ? stored : {};
    } catch {
      return {};
    }
  }

  function saveArtifactState(state) {
    try {
      localStorage.setItem(artifactStorageKey, JSON.stringify(state));
    } catch {
      // Progress persistence is optional when storage is unavailable.
    }
  }

  function updateArtifactProgress() {
    const completed = artifactBoxes.filter((box) => box.checked).length;
    if (artifactCount) {
      artifactCount.textContent = `${completed} of ${artifactBoxes.length} complete`;
    }
  }

  if (artifactBoxes.length) {
    const saved = readArtifactState();
    artifactBoxes.forEach((box) => {
      box.checked = Boolean(saved[box.dataset.artifact]);
      box.addEventListener("change", () => {
        const state = readArtifactState();
        state[box.dataset.artifact] = box.checked;
        saveArtifactState(state);
        updateArtifactProgress();
      });
    });
    updateArtifactProgress();
  }

  function updateProgress() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
  }

  function closeMenu({ restoreFocus = false } = {}) {
    document.body.classList.remove("nav-open");
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Open course navigation");
    scrim.hidden = true;
    if (restoreFocus) menuButton.focus();
  }

  function openMenu() {
    document.body.classList.add("nav-open");
    menuButton.setAttribute("aria-expanded", "true");
    menuButton.setAttribute("aria-label", "Close course navigation");
    scrim.hidden = false;
  }

  menuButton?.addEventListener("click", () => {
    const isOpen = document.body.classList.contains("nav-open");
    if (isOpen) closeMenu({ restoreFocus: true });
    else openMenu();
  });

  scrim?.addEventListener("click", () => closeMenu({ restoreFocus: true }));

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.matchMedia("(max-width: 920px)").matches) {
        closeMenu();
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && document.body.classList.contains("nav-open")) {
      closeMenu({ restoreFocus: true });
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 920) closeMenu();
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (!visible.length) return;
        const activeId = visible[0].target.id;
        navLinks.forEach((link) => {
          const isActive = link.getAttribute("href") === `#${activeId}`;
          link.classList.toggle("is-active", isActive);
          if (isActive) {
            link.setAttribute("aria-current", "location");
          } else {
            link.removeAttribute("aria-current");
          }
        });
      },
      {
        rootMargin: "-18% 0px -66% 0px",
        threshold: [0.01, 0.15, 0.35],
      }
    );
    sections.forEach((section) => observer.observe(section));
  }

  document.querySelectorAll(".code-block").forEach((block) => {
    const pre = block.querySelector("pre");
    if (!pre || !navigator.clipboard) return;

    const button = document.createElement("button");
    button.className = "copy-button";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy this code example");
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.innerText);
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1800);
      } catch {
        button.textContent = "Failed";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1800);
      }
    });
    block.append(button);
  });

  const labRoot = document.querySelector("#workflow-lab");
  if (labRoot) {
    const labCases = {
      churn: {
        label: "Customer churn",
        decisionOwner: "retention team",
        target: "whether a customer churns within 30 days",
        decisionTime: "at month-end, before the campaign starts",
        action: "prioritise a limited retention campaign",
        constraint: "campaign capacity covers 20% of customers",
        baselines: {
          capacity: "contact the top 20% by tenure",
          all: "contact every customer",
          none: "run no campaign",
        },
        errors: {
          miss: "missing a likely churner",
          false: "offering an unnecessary discount",
          balanced: "treating both errors as comparable",
        },
        features: [
          { label: "Tenure", leak: false },
          { label: "Monthly charge", leak: false },
          { label: "Cancellation reason", leak: true },
          { label: "Refund issued after cancel", leak: true },
        ],
        models: [
          { id: "baseline", name: "Tenure rule", detail: "Operational baseline", metrics: [["Recall", "61.2%"], ["Cost", "$40.0k"]] },
          { id: "candidate", name: "Logistic regression", detail: "Transparent candidate", metrics: [["Accuracy", "71.3%"], ["Precision", "62.8%"], ["Recall", "77.8%"]] },
          { id: "complex", name: "Decision tree", detail: "More complexity", metrics: [["Accuracy", "62.3%"], ["Precision", "54.1%"], ["Recall", "67.5%"]] },
        ],
      },
      house: {
        label: "House prices",
        decisionOwner: "property analyst",
        target: "the transaction price before a budget screen",
        decisionTime: "before the property enters the review shortlist",
        action: "filter properties for human review",
        constraint: "the screen happens before the sale closes",
        baselines: {
          capacity: "review only properties inside the current budget band",
          all: "review every listing",
          none: "use no automated screen",
        },
        errors: {
          miss: "missing a suitable property",
          false: "flagging an unsuitable property",
          balanced: "treating both review errors as comparable",
        },
        features: [
          { label: "Floor area", leak: false },
          { label: "Listing date", leak: false },
          { label: "Final sale price", leak: true },
          { label: "Post-sale price index", leak: true },
        ],
        models: [
          { id: "baseline", name: "Mean price", detail: "Naive baseline", metrics: [["MAE", "0.81"], ["RMSE", "1.02"]] },
          { id: "candidate", name: "Linear regression", detail: "Transparent candidate", metrics: [["MAE", "0.31"], ["RMSE", "0.44"]] },
          { id: "complex", name: "Random forest", detail: "More complexity", metrics: [["MAE", "0.47"], ["RMSE", "0.61"]] },
        ],
      },
      demand: {
        label: "Demand forecast",
        decisionOwner: "operations planner",
        target: "next month's unit demand",
        decisionTime: "before inventory and capacity are frozen",
        action: "set inventory and capacity",
        constraint: "the forecast is frozen before the month begins",
        baselines: {
          capacity: "use the same month last year",
          all: "hold maximum available inventory",
          none: "hold no safety inventory",
        },
        errors: {
          miss: "a stock-out after under-forecasting",
          false: "excess inventory after over-forecasting",
          balanced: "treating both forecast errors as comparable",
        },
        features: [
          { label: "Previous 12 months", leak: false },
          { label: "Calendar month", leak: false },
          { label: "Same-month actual sales", leak: true },
          { label: "Post-close demand revision", leak: true },
        ],
        models: [
          { id: "baseline", name: "Seasonal naive", detail: "Same month last year", metrics: [["MAPE", "10.62%"], ["MAE", "18.4"]] },
          { id: "candidate", name: "Seasonal linear", detail: "Trend plus season", metrics: [["MAPE", "2.86%"], ["MAE", "4.9"]] },
          { id: "complex", name: "Flexible tree", detail: "More complexity", metrics: [["MAPE", "4.10%"], ["MAE", "7.2"]] },
        ],
      },
    };

    const labState = {
      caseId: "churn",
      phase: "decision",
      pipelineMode: "safe",
      modelId: "candidate",
      selectedFeatures: new Set(["Tenure", "Monthly charge"]),
      threshold: 0.4,
      monitorMonth: 0,
    };

    const phaseNames = {
      decision: "Decision",
      leakage: "Data",
      pipeline: "Prepare",
      model: "Model",
      threshold: "Evaluate",
      monitoring: "Monitor",
    };

    const labStatus = document.querySelector("#lab-status");
    const coreLabel = document.querySelector("#workflow-core-label");
    const caseLabel = document.querySelector("#lab-case-label");
    const featureList = document.querySelector("#feature-list");
    const leakageOutput = document.querySelector("#leakage-output");
    const pipelineTrack = document.querySelector("#pipeline-track");
    const pipelineOutput = document.querySelector("#pipeline-output");
    const modelLadder = document.querySelector("#model-ladder");
    const modelReadout = document.querySelector("#model-readout");
    const thresholdRange = document.querySelector("#threshold-range");
    const thresholdValue = document.querySelector("#threshold-value");
    const thresholdMetrics = document.querySelector("#threshold-metrics");
    const thresholdOutput = document.querySelector("#threshold-output");
    const monitorRange = document.querySelector("#monitor-range");
    const monitorMonth = document.querySelector("#monitor-month");
    const monitorGrid = document.querySelector("#monitor-grid");
    const monitorOutput = document.querySelector("#monitor-output");
    const decisionOutput = document.querySelector("#decision-output");
    const decisionInsight = document.querySelector("#decision-insight");

    function announce(message) {
      labStatus.textContent = message;
    }

    function setActivePhase(target) {
      labState.phase = target;
      document.querySelectorAll("[data-lab-target]").forEach((button) => {
        const active = button.dataset.labTarget === target;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-selected", String(active));
        button.tabIndex = active ? 0 : -1;
      });
      document.querySelectorAll("[data-lab-panel]").forEach((panel) => {
        const active = panel.dataset.labPanel === target;
        panel.hidden = !active;
        panel.classList.toggle("is-active", active);
      });
      document.querySelectorAll("[data-workflow-node]").forEach((node) => {
        node.classList.toggle("is-active", node.dataset.workflowNode === target);
      });
      coreLabel.textContent = phaseNames[target];
      announce(`${phaseNames[target]} experiment ready`);
    }

    function renderDecision() {
      const current = labCases[labState.caseId];
      const metric = document.querySelector("#decision-metric").value;
      const baseline = document.querySelector("#decision-baseline").value;
      const error = document.querySelector("#decision-error").value;
      const metricLabels = {
        profit: "expected campaign profit",
        recall: "recall at the available contact capacity",
        accuracy: "overall classification accuracy",
      };
      decisionOutput.innerHTML = `<pre>For the ${current.decisionOwner}, estimate
${current.target}, ${current.decisionTime},
so that the team can ${current.action}.

Compare against: ${current.baselines[baseline]}.
Primary metric: ${metricLabels[metric]}.
Error focus: ${current.errors[error]}.
Constraint: ${current.constraint}.</pre>`;
      const warning =
        metric === "accuracy" && error !== "balanced"
          ? "Accuracy hides the cost asymmetry. Choose a metric that reflects the expensive error."
          : baseline === "none" && error === "false"
            ? "With no campaign, false offers cannot occur. This baseline does not test the proposed action."
            : "The brief links a decision, a baseline, a metric and the cost of error.";
      decisionInsight.textContent = warning;
      announce("Decision brief updated");
    }

    function renderFeatures() {
      const current = labCases[labState.caseId];
      featureList.innerHTML = current.features
        .map((feature) => {
          const selected = labState.selectedFeatures.has(feature.label);
          const leaked = selected && feature.leak;
          return `<button type="button" class="feature-chip${selected ? " is-selected" : ""}${leaked ? " is-leak" : ""}"
            data-feature="${feature.label}" aria-pressed="${selected}">${feature.label}</button>`;
        })
        .join("");
      const leaked = current.features.filter(
        (feature) => feature.leak && labState.selectedFeatures.has(feature.label),
      );
      leakageOutput.innerHTML = leaked.length
        ? `<strong>${leaked.length} field${leaked.length > 1 ? "s" : ""} would not exist at decision time.</strong>
           <p>${leaked.map((feature) => feature.label).join(", ")} turns apparent accuracy into hindsight. Remove the field or move the decision point later.</p>`
        : `<strong>The selected fields are available before the decision.</strong>
           <p>Now test whether their meaning, unit and update frequency are documented.</p>`;
      announce(leaked.length ? "Future-information leak detected" : "Feature timing valid");
    }

    function renderPipeline() {
      const current = labCases[labState.caseId];
      const safe = labState.pipelineMode === "safe";
      const steps = safe
        ? [
            ["01", "Split rows"],
            ["02", "Fit imputer"],
            ["03", "Fit scaler"],
            ["04", "Fit model"],
            ["05", "Score holdout"],
          ]
        : [
            ["01", "Fit scaler"],
            ["02", "Impute all rows"],
            ["03", "Split rows"],
            ["04", "Fit model"],
            ["05", "Score holdout"],
          ];
      pipelineTrack.innerHTML = steps
        .map(
          ([number, label], index) =>
            `<div class="pipeline-step${!safe && index < 3 ? " is-bad" : ""}"><b>${number}</b><strong>${label}</strong></div>`,
        )
        .join("");
      pipelineOutput.innerHTML = safe
        ? `<strong>The holdout remains untouched.</strong><p>Every learned transformation is fitted inside the training boundary. A clean rerun should reproduce the same row counts and parameters for ${current.label}.</p>`
        : `<strong>This score is contaminated.</strong><p>Scaling and imputation learned from the full dataset before the split. The pipeline runs, but the holdout no longer represents an unseen future decision.</p>`;
      document.querySelectorAll("[data-pipeline-mode]").forEach((button) => {
        const active = button.dataset.pipelineMode === labState.pipelineMode;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      announce(safe ? "Training boundary intact" : "Leaky preprocessing path");
    }

    function renderModel() {
      const current = labCases[labState.caseId];
      modelLadder.innerHTML = current.models
        .map(
          (model, index) =>
            `<button type="button" class="model-step${labState.modelId === model.id ? " is-active" : ""}"
              data-model-id="${model.id}" aria-pressed="${labState.modelId === model.id}">
              <span>Rung ${index + 1}</span><strong>${model.name}</strong><small>${model.detail}</small>
            </button>`,
        )
        .join("");
      const model = current.models.find((item) => item.id === labState.modelId) || current.models[1];
      modelReadout.innerHTML = model.metrics
        .map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`)
        .join("");
      if (labState.caseId === "churn" && labState.modelId === "complex") {
        modelReadout.insertAdjacentHTML(
          "beforeend",
          `<div><span>Verdict</span><strong>Baseline wins</strong></div>`,
        );
      }
      announce(`${model.name} selected`);
    }

    function renderThreshold() {
      const threshold = Number(labState.threshold);
      thresholdValue.textContent = threshold.toFixed(2);
      if (labState.caseId !== "churn") {
        thresholdRange.disabled = true;
        thresholdMetrics.innerHTML =
          `<div><span>Experiment</span><strong>Not applicable</strong></div>` +
          `<div><span>Reason</span><strong>Continuous target</strong></div>` +
          `<div><span>Use instead</span><strong>Error distribution</strong></div>`;
        thresholdOutput.textContent =
          "A classification threshold does not exist for this case. Switch to Customer churn to test a decision threshold.";
        announce("Threshold lab applies to classification");
        return;
      }
      thresholdRange.disabled = false;
      const precision = Math.min(0.91, 0.43 + threshold * 0.53);
      const recall = Math.max(0.38, 0.91 - threshold * 0.55);
      const expectedCost = Math.round((1 - recall) * 96 * 18 + (1 - precision) * 150 * 5);
      thresholdMetrics.innerHTML = `
        <div><span>Precision</span><strong>${(precision * 100).toFixed(1)}%</strong></div>
        <div><span>Recall</span><strong>${(recall * 100).toFixed(1)}%</strong></div>
        <div><span>Expected error cost</span><strong>$${expectedCost}k</strong></div>`;
      thresholdOutput.innerHTML =
        `<strong>${expectedCost > 86 ? "This operating point is expensive." : "This operating point balances both error types."}</strong>
         <p>At ${(threshold * 100).toFixed(0)}%, the team catches ${(recall * 100).toFixed(0)}% of churners and pays for the false alerts that remain. The choice belongs to the campaign owner.</p>`;
      announce(`Threshold changed to ${threshold.toFixed(2)}`);
    }

    function renderMonitoring() {
      const month = Number(labState.monitorMonth);
      const missing = 1.5 + Math.max(0, month - 2) * 0.55;
      const drift = Math.min(0.44, Math.max(0, month - 2) * 0.075);
      const liveRecall = Math.max(52, 77.8 - Math.max(0, month - 3) * 4.1);
      monitorMonth.textContent = String(month);
      monitorGrid.innerHTML = `
        <div class="${month >= 5 ? "is-alert" : ""}"><span>Missing charge</span><strong>${missing.toFixed(1)}%</strong></div>
        <div class="${month >= 4 ? "is-alert" : ""}"><span>Population drift</span><strong>${(drift * 100).toFixed(0)}%</strong></div>
        <div class="${month >= 6 ? "is-alert" : ""}"><span>Observed recall</span><strong>${liveRecall.toFixed(1)}%</strong></div>`;
      let message = "Inputs still match the reference period. Keep monitoring.";
      if (month >= 4) message = "Population drift crossed the review warning. Investigate the new customer mix.";
      if (month >= 6) message = "Observed recall has fallen materially. Pause automated decisions and retrain on current data.";
      monitorOutput.innerHTML = `<strong>Month ${month}: ${month >= 6 ? "retrain signal" : month >= 4 ? "review signal" : "no alert"}.</strong><p>${message} A monitoring chart without an owner and action is only latent evidence.</p>`;
      announce(`Monitoring month ${month}`);
    }

    function renderLabCase() {
      const current = labCases[labState.caseId];
      caseLabel.textContent = current.label;
      document.querySelector("#decision-baseline").options[0].textContent = current.baselines.capacity;
      document.querySelector("#decision-baseline").options[1].textContent = current.baselines.all;
      document.querySelector("#decision-baseline").options[2].textContent = current.baselines.none;
      document.querySelector("#decision-error").options[0].textContent = current.errors.miss;
      document.querySelector("#decision-error").options[1].textContent = current.errors.false;
      document.querySelector("#decision-error").options[2].textContent = current.errors.balanced;
      labState.selectedFeatures = new Set(
        current.features.filter((feature) => !feature.leak).slice(0, 2).map((feature) => feature.label),
      );
      document.querySelectorAll("[data-case-id]").forEach((button) => {
        const active = button.dataset.caseId === labState.caseId;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      renderDecision();
      renderFeatures();
      renderPipeline();
      renderModel();
      renderThreshold();
      renderMonitoring();
      announce(`${current.label} loaded`);
    }

    document.querySelectorAll("[data-lab-target]").forEach((button) => {
      button.addEventListener("click", () => setActivePhase(button.dataset.labTarget));
      button.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        const buttons = Array.from(document.querySelectorAll("[data-lab-target]"));
        const currentIndex = buttons.indexOf(button);
        const nextIndex =
          event.key === "Home"
            ? 0
            : event.key === "End"
              ? buttons.length - 1
              : (currentIndex + (event.key === "ArrowRight" || event.key === "ArrowDown" ? 1 : -1) + buttons.length) %
                buttons.length;
        buttons[nextIndex].focus();
        setActivePhase(buttons[nextIndex].dataset.labTarget);
      });
    });

    document.querySelectorAll("[data-case-id]").forEach((button) => {
      button.addEventListener("click", () => {
        labState.caseId = button.dataset.caseId;
        renderLabCase();
      });
    });

    ["#decision-metric", "#decision-baseline", "#decision-error"].forEach((selector) => {
      document.querySelector(selector).addEventListener("change", renderDecision);
    });

    featureList.addEventListener("click", (event) => {
      const chip = event.target.closest("[data-feature]");
      if (!chip) return;
      const feature = chip.dataset.feature;
      if (labState.selectedFeatures.has(feature)) {
        labState.selectedFeatures.delete(feature);
      } else {
        labState.selectedFeatures.add(feature);
      }
      renderFeatures();
    });

    document.querySelectorAll("[data-pipeline-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        labState.pipelineMode = button.dataset.pipelineMode;
        renderPipeline();
      });
    });

    modelLadder.addEventListener("click", (event) => {
      const button = event.target.closest("[data-model-id]");
      if (!button) return;
      labState.modelId = button.dataset.modelId;
      renderModel();
    });

    thresholdRange.addEventListener("input", () => {
      labState.threshold = thresholdRange.value;
      renderThreshold();
    });

    monitorRange.addEventListener("input", () => {
      labState.monitorMonth = monitorRange.value;
      renderMonitoring();
    });

    renderLabCase();
  }

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      window.requestAnimationFrame(() => {
        updateProgress();
        ticking = false;
      });
      ticking = true;
    },
    { passive: true }
  );

  updateProgress();

  if (!reduceMotion && "IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 }
    );
    document.querySelectorAll(".outcome-card, .case-study .figure-panel").forEach((element) => {
      element.classList.add("reveal");
      revealObserver.observe(element);
    });
  }
})();
