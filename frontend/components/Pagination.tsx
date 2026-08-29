'use client';

import { cn } from '@/shared/lib/utils';

// Define inputs to the Prop
type Props = {
    currentPage: number; // 0-indexed
    totalPages: number;
    onPageChange: (page: number) => void;
};

const BUTTON_STYLING = 'rounded-md border border-main bg-white px-3 py-1.5 text-sm disabled:opacity-40 disabled:cursor-not-allowed';
const PAGE_JUMP = 10;


export function Pagination({ currentPage, totalPages, onPageChange }: Props) {
    if (totalPages <= 1) return null;

    const windowStart = Math.max(0, Math.min(currentPage - 1, totalPages - 3));
    const windowEnd = Math.min(totalPages - 1, windowStart + 2);
    const pageNumbers = Array.from(
        { length: windowEnd - windowStart + 1},
        (_, i) => windowStart + i
    );

    const isFirst = currentPage === 0;
    const isLast = currentPage === totalPages - 1;

    return (
        <div className='pagination flex items-center gap-1 ml-2 mb-2'>
            <button className={BUTTON_STYLING} onClick={() => onPageChange(0)} disabled={isFirst} aria-label='First page'>«</button>
            <button className={BUTTON_STYLING} onClick={() => onPageChange(currentPage - 1)} disabled={isFirst} aria-label='Previous page'>‹</button>

            {windowStart > 0 && (
                <button
                    className={BUTTON_STYLING}
                    onClick={() => onPageChange(Math.max(0, currentPage - PAGE_JUMP))}
                    aria-label={`Back ${PAGE_JUMP} pages`}
                >
                    ...
                </button>
            )}

            {pageNumbers.map((p) => (
                <button
                    key={`page-${p}`}
                    className={cn(BUTTON_STYLING, p === currentPage && 'bg-foreground text-background')}
                    onClick={() => onPageChange(p)}
                    aria-current={p === currentPage ? 'page': undefined}
                >
                    {p + 1}
                </button>
            ))}

            {windowEnd < totalPages - 1 && (
                <button
                    className={BUTTON_STYLING}
                    onClick={() => onPageChange(Math.min(totalPages - 1, currentPage + PAGE_JUMP))}
                    aria-label={`Forward ${PAGE_JUMP} pages`}
                >
                    ...
                </button>
            )}

            <button className={BUTTON_STYLING} onClick={() => onPageChange(currentPage + 1)} disabled={isLast} aria-label='Next page'>›</button>
            <button className={BUTTON_STYLING} onClick={() => onPageChange(totalPages - 1)} disabled={isLast} aria-label='Last page'>»</button>
            
        </div>
    )
}