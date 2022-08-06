import {useEffect, useState} from 'react';

export default function JudgeWikipedia() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [item, setItem] = useState({});
    const [items, setItems] = useState([
        {
            id: 1,
            title: 'rendang pedas udang galah kacang buncis',
            definitions: {
                id: 'Masakan daging asli Indonesia yang berasal dari Minangkabau',
                ms: 'Masakan daging asli Indonesia yang berasal dari Minangkabau',
                en: ''
            }
        },
        {
            id: 2,
            title: 'Test 2',
            definitions: {
                id: 'definisi dari id.wiki',
                ms: 'definisi dari ms.wiki',
                en: 'definisi dari en.wiki'
            }
        },
        {
            id: 3,
            title: 'Test 3',
            definitions: {
                id: 'definisi dari id.wiki',
                en: 'definisi dari en.wiki'
            }
        },
    ]);

    useEffect(() => {
        setItem(items[currentIndex]);
    }, [currentIndex]);

    return <div className="mx-6 p-6 bg-lime-100 rounded">
        <div className="mb-4">
            <div className="rounded h-2 bg-white mb-1">
                <div className="h-2 rounded bg-lime-500"
                     style={{width: `${100 * (currentIndex + 1) / items.length}%`}}/>
            </div>
            <div className="text-sm text-lime-900 text-center">{currentIndex + 1} of {items.length}</div>
        </div>

        <h1 className="text-center text-xl font-bold mb-3 uppercase">{item.title}</h1>

        <div className={"mb-3 bg-lime-50 border rounded border-lime-200 p-3 " + (item.definitions?.id? '': 'hidden')}>
            {item.definitions?.id}
            <div className="text-lime-500 text-right">id.wikipedia.org</div>
        </div>

        <div className={"mb-3 bg-lime-50 border rounded border-lime-200 p-3 " + (item.definitions?.ms? '': 'hidden')}>
            {item.definitions?.ms}
            <div className="text-lime-500 text-right">my.wikipedia.org</div>
        </div>

        <div className={"mb-3 bg-lime-50 border rounded border-lime-200 p-3 " + (item.definitions?.en? '': 'hidden')}>
            {item.definitions?.en}
            <div className="text-lime-500 text-right">en.wikipedia.org</div>
        </div>

        <div className="mt-5">Please suggest categories based on description above:</div>
        <input type="text" className="w-full rounded px-3 my-2 py-1" name="" placeholder="fish, spice"/>
        <div className="text-sm text-lime-800">Separate multiple categories with comma.</div>

        <div className="mt-3">
            <button onClick={() => setCurrentIndex(n => n === 0 ? 0 : n - 1)}
                    disabled={currentIndex === 0}
                    className="btn rounded text-white bg-lime-500 mr-1 disabled:opacity-50">Prev
            </button>
            <button onClick={() => setCurrentIndex(n => n < items.length - 1 ? n + 1 : n)}
                    disabled={currentIndex === items.length - 1}
                    className="btn rounded text-white bg-lime-500 mr-1 disabled:opacity-50">Next
            </button>
        </div>

    </div>
}