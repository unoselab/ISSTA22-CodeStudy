declare function require(name: string): any;

declare const process: {
    argv: string[];
    exit(code?: number): never;
};

const cp = require('child_process');
const fs = require('fs');
const path = require('path');

type SummaryItem = {
    summary: string;
    probability: number;
};

function runSummarizeProcess(
    python: string,
    scriptPath: string,
    code: string
): Promise<SummaryItem[]> {
    return new Promise((resolve, reject) => {
        const proc = cp.spawn(python, [scriptPath, '--json', '--stdin'], {
            windowsHide: true,
        });

        let out = '';
        let err = '';
        let settled = false;

        const fail = (e: Error) => {
            if (!settled) {
                settled = true;
                reject(e);
            }
        };

        const succeed = (items: SummaryItem[]) => {
            if (!settled) {
                settled = true;
                resolve(items);
            }
        };

        proc.stdout.setEncoding('utf8');
        proc.stderr.setEncoding('utf8');

        proc.stdout.on('data', (chunk: string) => {
            out += chunk;
        });

        proc.stderr.on('data', (chunk: string) => {
            err += chunk;
        });

        proc.on('error', (e: Error) => fail(e));
        proc.stdin.on('error', (e: Error) => fail(e));

        proc.on('close', (exitCode: number | null) => {
            if (exitCode !== 0) {
                fail(new Error(err.trim() || `Summarizer exited with code ${exitCode}`));
                return;
            }

            try {
                const parsed = JSON.parse(out.trim()) as SummaryItem[];
                succeed(parsed);
            } catch {
                fail(
                    new Error(
                        `Failed to parse summarizer JSON.\nstdout: ${out.trim() || '<empty>'}\nstderr: ${err.trim() || '<empty>'}`
                    )
                );
            }
        });

        proc.stdin.end(code, 'utf8');
    });
}

async function main(): Promise<void> {
    const python = process.argv[2] || 'python';
    const scriptPath = process.argv[3] || './summarizer.py';
    const inputFile = process.argv[4];

    let code: string;

    if (inputFile) {
        code = fs.readFileSync(path.resolve(inputFile), 'utf8');
    } else {
        code = `
def add(a, b):
    return a + b
`.trim();
    }

    try {
        const results = await runSummarizeProcess(python, path.resolve(scriptPath), code);
        console.log(JSON.stringify(results, null, 2));
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        console.error('Error:', message);
        process.exit(1);
    }
}

main();