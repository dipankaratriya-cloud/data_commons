import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { url } = body;

        if (!url) {
            return NextResponse.json({ success: false, error: 'URL is required' }, { status: 400 });
        }

        // Path to the python script
        // Assuming the script is in the root/scripts directory relative to the project root
        // We need to go up from frontend/src/app/api/extract to root
        const scriptPath = path.resolve(process.cwd(), '../scripts/extract.py');

        // Execute the python script
        // Using python3, assuming it's in the path and has the required dependencies
        const command = `python3 "${scriptPath}" --url "${url}"`;

        console.log(`Executing command: ${command}`);

        const { stdout, stderr } = await execAsync(command);

        if (stderr) {
            console.error(`Script stderr: ${stderr}`);
            // Note: stderr might contain warnings, not necessarily fatal errors
            // We'll rely on stdout parsing to check for success
        }

        try {
            const result = JSON.parse(stdout);
            return NextResponse.json(result);
        } catch (parseError) {
            console.error('Failed to parse script output:', stdout);
            return NextResponse.json({
                success: false,
                error: 'Failed to parse script output',
                raw_output: stdout
            }, { status: 500 });
        }

    } catch (error) {
        console.error('API Error:', error);
        return NextResponse.json({
            success: false,
            error: error instanceof Error ? error.message : 'Internal server error'
        }, { status: 500 });
    }
}
