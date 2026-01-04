import './globals.css';

export const metadata = {
    title: 'AI Letter Writer',
    description: 'Generate letters that sound exactly like you.',
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
