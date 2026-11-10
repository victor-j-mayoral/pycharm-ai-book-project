import { pipeline } from '@huggingface/transformers';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';


export type SearchResult = {
    snippet: string,
    filePath: string,
    score: number
};

interface SavedIndex {
    modelName: string;
    index: number[][];
    snippets: string[];
    paths: string[];
}

type Embedder = (
    texts: string[]
) => Promise<number[][]>;


export class CodeSearchEngine {
    private index: number[][] | null = null;
    private codeSnippets: string[] = [];
    private filePaths: string[] = [];

    private constructor(
        private readonly embed: Embedder,
        private readonly modelName: string,
        private readonly indexPath: string
    ) {
        this.index = null;
        this.codeSnippets = [];
        this.filePaths = [];
    }

    // Model initialization is asynchronous.
    static async create(
        indexPath: string,
        modelName = 'Xenova/all-MiniLM-L6-v2'
    ): Promise<CodeSearchEngine> {
        const extractor = await pipeline(
            'feature-extraction',
            modelName
        );

        const embed: Embedder = async texts => {
            const output = await extractor(texts, {
                pooling: 'mean',
                normalize: true
            });

            return output.tolist() as number[][];
        };

        return new CodeSearchEngine(embed, modelName, indexPath);
    }

    async indexCodebase(rootDirectory: string): Promise<void> {
        // Build a fresh index to avoid duplicates on repeated indexing.
        const snippets: string[] = [];
        const filePaths: string[] = [];

        const excluded = new Set([
            '.git',
            '__pycache__',
            'node_modules',
            'venv',
            '.venv'
        ]);

        const walk = async (directory: string): Promise<void> => {
            const entries = await fs.readdir(directory, {
                withFileTypes: true
            });

            for (const entry of entries) {
                const filePath = path.join(directory, entry.name);

                if (entry.isDirectory()) {
                    if (!excluded.has(entry.name)) {
                        await walk(filePath);
                    }
                    continue;
                }

                if (!entry.isFile() || !entry.name.endsWith('.py')) {
                    continue;
                }

                try {
                    const content = await fs.readFile(filePath, 'utf8');
                    const chunks = this.splitCodeIntoChunks(content);

                    for (const chunk of chunks) {
                        snippets.push(chunk);
                        filePaths.push(filePath);
                    }
                } catch (error) {
                    console.error(`Error indexing ${filePath}:`, error);
                }
            }
        };

        await walk(path.resolve(rootDirectory));

        // Small batches limit memory usage.
        const embeddings: number[][] = [];
        const batchSize = 16;

        for (let i = 0; i < snippets.length; i += batchSize) {
            embeddings.push(
                ...await this.embed(snippets.slice(i, i + batchSize))
            );
        }

        this.codeSnippets = snippets;
        this.filePaths = filePaths;
        this.index = embeddings;

        await this.saveIndex();
    }

    splitCodeIntoChunks(code: string): string[] {
        const chunks: string[] = [];
        let currentChunk: string[] = [];

        for (const line of code.split(/\r?\n/)) {
            const stripped = line.trimStart();

            if (!stripped) {
                currentChunk.push(line);
                continue;
            }

            const currentIndent = line.length - stripped.length;
            const isDefinition = /^(def |async def |class )/.test(stripped);

            if (isDefinition && currentIndent === 0) {
                if (currentChunk.join('\n').trim()) {
                    chunks.push(currentChunk.join('\n'));
                }
                currentChunk = [line];
            } else {
                currentChunk.push(line);
            }
        }

        if (currentChunk.join('\n').trim()) {
            chunks.push(currentChunk.join('\n'));
        }

        return chunks;
    }

    async search(
        query: string,
        topK = 5
    ): Promise<SearchResult[]> {
        if (!this.index?.length || topK <= 0) {
            return [];
        }

        const [queryEmbedding] = await this.embed([query]);

        // Normalized vectors: dot product equals cosine similarity.
        return this.index
            .map((embedding, i) => ({
                index: i,
                score: embedding.reduce(
                    (sum, value, j) => sum + value * queryEmbedding[j],
                    0
                )
            }))
            .sort((a, b) => b.score - a.score)
            .slice(0, Math.floor(topK))
            .map(({ index, score }): SearchResult => ({
                snippet: this.codeSnippets[index],
                filePath: this.filePaths[index],
                score
            }));
    }

    async saveIndex(filePath = this.indexPath): Promise<void> {
        await fs.mkdir(path.dirname(filePath), { recursive: true });

        const data: SavedIndex = {
            modelName: this.modelName,
            index: this.index ?? [],
            snippets: this.codeSnippets,
            paths: this.filePaths
        };

        await fs.writeFile(filePath, JSON.stringify(data), 'utf8');
    }

    async loadIndex(filePath = this.indexPath): Promise<boolean> {
        let content: string;

        try {
            content = await fs.readFile(filePath, 'utf8');
        } catch (error) {
            if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
                return false;
            }
            throw error;
        }

        const data = JSON.parse(content) as SavedIndex;

        if (data.modelName !== this.modelName) {
            throw new Error('Index model mismatch. Reindex the codebase.');
        }

        if (
            !Array.isArray(data.index) ||
            !Array.isArray(data.snippets) ||
            !Array.isArray(data.paths) ||
            data.index.length !== data.snippets.length ||
            data.index.length !== data.paths.length
        ) {
            throw new Error('Invalid search index.');
        }

        this.index = data.index;
        this.codeSnippets = data.snippets;
        this.filePaths = data.paths;

        return true;
    }
}