import './globals.css';

export const metadata = {
    title: 'AI Letter Engine',
    description: 'Self-Learning RAG Letter Generator',
}

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    )
}
