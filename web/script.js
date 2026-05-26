let selectedBonusFiles = [];

function comutaTab(idTab) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('block');
        tab.classList.add('hidden');
    });

    const tabs = ['transactions', 'financial', 'logins', 'bonus', 'se-history', 'communications', 'dep-limit'];
    tabs.forEach(t => {
        document.getElementById(`btn-tab-${t}`).className = "flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-all text-slate-400 hover:bg-slate-800 min-w-[150px]";
    });

    document.getElementById(idTab).classList.remove('hidden');
    document.getElementById(idTab).classList.add('block');

    const activeBtn = 'btn-' + idTab;
    document.getElementById(activeBtn).className = "flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-all bg-emerald-500 text-slate-950 shadow min-w-[150px]";
}

function toggleSetariVizuale() {
    const body = document.getElementById('corp-setari-vizuale');
    const arrow = document.getElementById('sageata-setari');
    body.classList.toggle('hidden');
    arrow.innerText = body.classList.contains('hidden') ? "👇" : "👆";
}

async function deschideExplorator(idInputDestinatie) {
    let path = await eel.selecteaza_fisier_local()();
    if (path && path.length > 0) {
        document.getElementById(idInputDestinatie).value = Array.isArray(path) ? path[0] : path;
    }
}

async function deschideExploratorMultiplu(idInputDestinatie) {
    let paths = await eel.selecteaza_fisier_local()();
    if (paths && paths.length > 0) {
        selectedBonusFiles = paths;
        document.getElementById(idInputDestinatie).value = `Selected ${paths.length} source file(s) ready for consolidation.`;
    }
}

async function lanseazaProcesare(tipTab) {
    let idInput;
    if (tipTab === 'transactions') idInput = 'cale-tab1';
    else if (tipTab === 'financial') idInput = 'cale-tab2';
    else if (tipTab === 'logins') idInput = 'cale-tab3';
    else if (tipTab === 'communications') idInput = 'cale-tab4';
    else if (tipTab === 'bonus') idInput = 'cale-tab5';
    else if (tipTab === 'se-history') idInput = 'cale-tab6';
    else if (tipTab === 'dep-limit') idInput = 'cale-tab7';
    else idInput = null;

    if (idInput) {
        const filePath = document.getElementById(idInput).value;
        if (!filePath) {
            alert("Please select a valid data file using the 'Browse...' button first!");
            return;
        }
    }

    const requiresPassword = document.getElementById('cfg-paroleaza').checked;
    const sourceTaxId = document.getElementById('cfg-cnp').value.trim();

    if (requiresPassword && (!sourceTaxId || sourceTaxId.length < 6)) {
        alert("⚠️ WARNING: A valid Tax ID / Identification Code is required in global settings!\n\nTo generate secured PDFs, a reference code is needed to extract the last 6 security digits.");
        return;
    }

    const pageSize = document.getElementById('dimensiune-pagina').value;
    const pageOrientation = document.getElementById('orientare-pagina').value;

    const dateAntet = {
        nume: document.getElementById('cfg-nume').value,
        cnp: sourceTaxId,
        email: document.getElementById('cfg-email').value,
        companie: document.getElementById('cfg-companie').value,
        text_intro: document.getElementById('cfg-intro').value,
        paroleaza_pdf: requiresPassword
    };

    const dateSubsol = {
        text_declaratie: document.getElementById('cfg-declaratie').value,
        text_copyright: document.getElementById('cfg-copyright').value
    };

    const btn = document.getElementById(`btn-executa-${tipTab}`);
    const statusRegion = document.getElementById('zona-status');

    btn.disabled = true;
    btn.classList.add('opacity-50');
    statusRegion.classList.remove('hidden');

    let result;
    if (tipTab === 'transactions') {
        const filePath = document.getElementById(idInput).value;
        const exportMonths = document.getElementById('chk-export-luni').checked;
        result = await eel.proceseaza_tab_transactions(filePath, pageSize, pageOrientation, dateAntet, dateSubsol, exportMonths)();
    } else if (tipTab === 'financial') {
        const filePath = document.getElementById(idInput).value;
        result = await eel.proceseaza_tab_financial(filePath, pageSize, pageOrientation, dateAntet, dateSubsol)();
    } else if (tipTab === 'logins') {
        const filePath = document.getElementById(idInput).value;
        result = await eel.proceseaza_tab_logins(filePath, pageSize, pageOrientation, dateAntet, dateSubsol)();
    } else if (tipTab === 'communications') {
        const filePath = document.getElementById(idInput).value;
        result = await eel.proceseaza_tab_communications(filePath, pageSize, pageOrientation, dateAntet, dateSubsol)();
    } else if (tipTab === 'bonus') {
        result = await eel.proceseaza_tab_bonus(selectedBonusFiles, pageSize, pageOrientation, dateAntet, dateSubsol)();
    } else if (tipTab === 'se-history') {
        const filePath = document.getElementById(idInput).value;
        result = await eel.proceseaza_tab_se_history(filePath, pageSize, pageOrientation, dateAntet, dateSubsol)();
    } else if (tipTab === 'dep-limit') {
        const filePath = document.getElementById(idInput).value;
        result = await eel.proceseaza_tab_dep_limit_history(filePath, pageSize, pageOrientation, dateAntet, dateSubsol)();
    }

    btn.disabled = false;
    btn.classList.remove('opacity-50');
    statusRegion.classList.add('hidden');

    if (result.succes) {
        let securityStatus = requiresPassword ? `🔒 Document structure secured using the last 6 characters of the Identification Code (${sourceTaxId.slice(-6)}).` : "🔓 Report exported WITHOUT encryption.";

        if (result.multiple) {
            let filesList = result.fisiere.join("\n• ");
            alert(`Success! Generated ${result.fisiere.length} monthly reports inside the export directory:\n\n• ${filesList}\n\n${securityStatus}`);
        } else {
            alert(`Execution Successful!\nThe official report has been compiled and saved into 'PDF_Reports_Export'.\n👉 Target File: ${result.cale}\n${securityStatus}`);
        }
    } else {
        alert(`An error occurred during pipeline execution:\n${result.eroare}`);
    }
}

eel.expose(actualizeazaStatus);
function actualizeazaStatus(mesaj) {
    document.getElementById('text-status').innerText = mesaj;
}