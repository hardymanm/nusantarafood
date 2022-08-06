import {useEffect, useState} from 'react';

export default function JudgeTabel() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [item, setItem] = useState({});
    const [items, setItems] = useState([
        {
            id: 1,
            title: 'udang goreng garam kunyit',
            categories: [
                {name: 'fish', selected: true},
                {name: 'spice', selected: false},
            ]
        },
        {
            id: 1,
            title: 'udang goreng',
            categories: [
                {name: 'fish', selected: true},
                {name: 'spice', selected: true},
            ]
        },
        {
            id: 1,
            title: 'ikan panggang',
            categories: [
                {name: 'fish', selected: true},
                {name: 'spice', selected: false},
            ]
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

        <div className="mb-3">Please select or suggest correct categories:</div>

        {item.categories?.map(category => {
            const txt = category.selected? 'text-white': 'text-lime-500';
            const cls = 'h-6 w-6 inline-block mr-2 ' + txt;

            return <div className="bg-lime-500 rounded text-white p-3 mb-3 cursor-pointer hover:opacity-75">
                <svg xmlns="http://www.w3.org/2000/svg" className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <strong>{category.name}</strong>
            </div>
        })}

        <div className="mt-5">Suggest categories:</div>
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