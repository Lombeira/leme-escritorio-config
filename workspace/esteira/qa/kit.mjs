// Kit de QA da esteira (leme-app em homolog). Leia esteira/qa/CONHECIMENTO.md antes de usar.
//
// Rode os scripts com:
//   QA_BASE=http://127.0.0.1:530x QA_WORKTREE=<worktree do card> QA_CARD=<KEY> node meu-script.mjs
// e importe:
//   import { abrirNavegador, salvarPrint, urlEscopo } from "/home/leme/workspace/esteira/qa/kit.mjs";
import { mkdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";

// Variáveis de ambiente não persistem entre chamadas da ferramenta Bash (LM-2800). Sem elas, o kit
// lê ./qa.json da pasta onde o script roda: {"base": "...", "worktree": "...", "card": "LM-n"}.
const arquivoLocal = (() => {
	try {
		return JSON.parse(readFileSync(`${process.cwd()}/qa.json`, "utf8"));
	} catch {
		return {};
	}
})();
export const BASE = (process.env.QA_BASE ?? arquivoLocal.base ?? "http://127.0.0.1:5301").replace(/\/$/, "");
export const WORKTREE = process.env.QA_WORKTREE ?? arquivoLocal.worktree;
export const CARD = process.env.QA_CARD ?? arquivoLocal.card;
export const EVID = CARD ? `${homedir()}/workspace/.escritorio/cards/${CARD}/evidencias` : null;

// O Playwright vem do node_modules do worktree do card (o kit não tem dependências próprias).
export function playwright() {
	if (!WORKTREE) throw new Error("defina QA_WORKTREE (worktree do card)");
	return createRequire(`${WORKTREE}/package.json`)("@playwright/test");
}

// Contas de teste de homolog. A senha só existe em memória: nunca imprima nem grave.
export function contas() {
	const env = {};
	const arq = `${homedir()}/.config/leme-escritorio/qa.env`;
	for (const linha of readFileSync(arq, "utf8").split("\n")) {
		const m = linha.match(/^([A-Z_]+)=(.*)$/);
		if (m) env[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
	}
	return env;
}

// Login pela API (pelo proxy /api do dev server). Bom para preparar e conferir dados sem tela.
export async function loginApi(papel = "ADMIN") {
	const env = contas();
	const res = await fetch(`${BASE}/api/auth/login`, {
		method: "POST",
		headers: { "content-type": "application/json", accept: "application/json" },
		body: JSON.stringify({ email: env[`QA_${papel}_EMAIL`].toLowerCase(), password: env.QA_PASSWORD }),
	});
	if (!res.ok) throw new Error(`login ${papel}: HTTP ${res.status}`);
	return (await res.json()).token;
}

export function api(token) {
	return async (caminho, opts = {}) => {
		const res = await fetch(`${BASE}/api/${caminho.replace(/^\//, "")}`, {
			...opts,
			headers: {
				accept: "application/json",
				"content-type": "application/json",
				authorization: `Bearer ${token}`,
				...(opts.headers ?? {}),
			},
		});
		const texto = await res.text();
		let corpo = texto;
		try {
			corpo = JSON.parse(texto);
		} catch {}
		return { status: res.status, corpo };
	};
}

// Escola/ano/turma vivem na query string (requisito de link compartilhável).
export function urlEscopo(caminho, { escola, ano, turma } = {}) {
	const q = new URLSearchParams();
	if (escola) q.set("school", escola);
	if (ano) q.set("year", ano);
	if (turma) q.set("class", turma);
	const s = q.toString();
	return `${BASE}${caminho}${s ? `?${s}` : ""}`;
}

// Navegador já logado. errosConsole junta erros de console e de página depois do login.
export async function abrirNavegador({ papel = "ADMIN", largura = 1440, altura = 900 } = {}) {
	const { chromium } = playwright();
	const env = contas();
	const browser = await chromium.launch({ headless: true });
	const context = await browser.newContext({
		viewport: { width: largura, height: altura },
		locale: "pt-BR",
		timezoneId: "America/Sao_Paulo",
	});
	const page = await context.newPage();
	const errosConsole = [];
	page.on("console", (m) => m.type() === "error" && errosConsole.push(m.text()));
	page.on("pageerror", (e) => errosConsole.push(`pageerror: ${e.message}`));
	await page.goto(`${BASE}/`);
	await page.getByLabel("Email").fill(env[`QA_${papel}_EMAIL`]);
	await page.getByRole("textbox", { name: "Senha" }).fill(env.QA_PASSWORD);
	await page.getByRole("button", { name: "Acessar" }).click();
	await page.waitForURL(/dashboard/, { timeout: 60000 }); // primeira carga do Vite é lenta
	errosConsole.length = 0;
	return { browser, context, page, errosConsole };
}

// Flags reais do GrowthBook de homolog/dev, direto do CDN. Ouvir a rede da página não funciona:
// o SDK usa cache e outra URL (LM-2800). A chave é a client key pública que vai no bundle do front.
export const GROWTHBOOK_URL = "https://cdn.growthbook.io/api/features/sdk-PfBA0nDoUz18QDn8";

export async function lerFlags() {
	const res = await fetch(GROWTHBOOK_URL);
	if (!res.ok) throw new Error(`GrowthBook: HTTP ${res.status}`);
	const flags = {};
	for (const [nome, def] of Object.entries((await res.json()).features ?? {})) flags[nome] = def?.defaultValue;
	return flags;
}

// Força flags só neste navegador (override do próprio app), sem tocar em dado nenhum. Recarrega a
// página para valer. Ex.: forcarFlags(page, { IsMapaLemeEnabled: [{ id, name }], "is-mapa-v2-enabled": [] })
// ([] em is-mapa-v2-enabled força o Mapa V1).
export async function forcarFlags(page, overrides) {
	await page.evaluate((o) => localStorage.setItem("leme:gb-overrides", JSON.stringify(o)), overrides);
	await page.reload();
}

export async function salvarPrint(page, nome, { paginaInteira = true } = {}) {
	if (!EVID) throw new Error("defina QA_CARD para salvar evidências");
	mkdirSync(EVID, { recursive: true });
	const caminho = `${EVID}/${nome.replace(/\.png$/, "")}.png`;
	await page.screenshot({ path: caminho, fullPage: paginaInteira });
	return caminho;
}
