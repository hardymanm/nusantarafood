import {Link} from "react-router-dom";

function JudgeLink({to, children, alt}) {
    return <div className="w-full md:w-1/3 mb-8">
        <Link to={to} className="flex justify-center">
            <div>
                <div className="w-24 h-24 bg-lime-200 rounded-full mb-2"/>
                <div className="text-center">{children}</div>
            </div>

        </Link>
    </div>
}

export default function Home() {
    return <>
        <div className="h-96 grid place-content-center bg-cover bg-center bg-lime-500">
            <div className="text-center px-5">
                <h1 className={'sm:text-3xl text-2xl font-medium text-white mb-4 uppercase'}>
                    We help your business
                </h1>
                <h5 className="mb-4 text-lime-200">
                    It is a long established fact that a reader will be distracted by the readable content of a page
                    when looking at its layout
                </h5>

                <button
                    className="transition bg-lime-200 text-lime-600 px-6 py-3 rounded hover:opacity-80 active:opacity-75 duration-300">
                    LEARN MORE
                </button>
            </div>
        </div>

        <div className="mt-10 px-5">
            <h3 className="text-lg font-medium text-gray-900 mb-10 text-center uppercase">
                How to judge the ontology
            </h3>

            <div className="flex flex-wrap">
                <JudgeLink to="/judge/dataset-wordnet" alt="wordnet">WordNet</JudgeLink>
                <JudgeLink to="/judge/dataset-wikipedia" alt="wordnet">Wikipedia</JudgeLink>
                <JudgeLink to="/judge/dataset-tabel" alt="wordnet">DKPI</JudgeLink>
            </div>
        </div>
    </>
}