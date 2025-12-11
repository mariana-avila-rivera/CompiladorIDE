module Main where

import System.Environment
import System.IO
import Data.Array
import Data.IORef
import Control.Monad
import Text.Printf

import Types
import VirtualMachine
import ReadTMcode

main :: IO ()
main = do
    args <- getArgs
    if (length args) /= 2 
        then 
            error "Incorrect number of parameters. Parameters required are 1) filename of TM instruction file and 2) dmem maximum address.\n"
        else
            return ()
    tmCodeFile <- return $ ((args !! 0) :: String)
    dmemMaxAddr <- return $ (read (args !! 1) :: Int)
 
    program <- readProgramFromFile tmCodeFile
    
    let initState = initTMstate program dmemMaxAddr
    
    putStrLn "Starting TMVS CLI..."
    runLoop initState

runLoop :: TMstate -> IO ()
runLoop state = do
    let newState = performTMstep state
    let result = getTMstateStepResult newState
    
    case result of
        TMokay -> runLoop newState
        
        TMhalt -> do
            putStrLn "HALT: Execution finished."
            
        TMinputReq r -> do
            -- Get previous instruction to find the variable name
            let regs = getTMstateRegs newState
            let pcVal = floor (regs ! 7) -- PC is register 7
            let prevPc = pcVal - 1
            let imem = getTMstateimem newState
            let inst = imem ! prevPc
            let varName = extractVarName inst
            
            if varName == ""
                then putStr $ "Input required for register " ++ (show r) ++ ": "
                else putStr $ varName ++ " = "
            
            hFlush stdout
            inputStr <- getLine
            -- Add a newline to separate input from subsequent output in case of pipe buffering issues
            putStrLn ""
            let val = read inputStr :: Double
            let regs = getTMstateRegs newState
            let newRegs = regs // [(r, val)]
            -- Reset result to TMokay so we can continue
            let stateWithInput = newState { getTMstateRegs = newRegs, getTMstateStepResult = TMokay }
            runLoop stateWithInput
            
        TMoutput val -> do
            let outStr = if val == fromInteger (round val) 
                         then show (round val :: Integer)
                         else show val
            
            -- Get previous instruction to find the variable name
            let regs = getTMstateRegs newState
            let pcVal = floor (regs ! 7)
            let prevPc = pcVal - 1
            let imem = getTMstateimem newState
            let inst = imem ! prevPc
            let varName = extractVarName inst
            
            if varName == "" 
                then putStrLn $ "out = " ++ outStr
                else putStrLn $ "out " ++ varName ++ " = " ++ outStr

            -- Reset result to TMokay so we can continue
            let stateAck = newState { getTMstateStepResult = TMokay }
            runLoop stateAck
            
        TMiMemError addr -> do
            putStrLn $ "Error: Instruction Memory Access Error at address " ++ (show addr)
            
        TMdMemError addr -> do
            putStrLn $ "Error: Data Memory Access Error at address " ++ (show addr)
            
        TMzeroDivide -> do
            putStrLn "Error: Division by Zero"

extractVarName :: Instruction -> String
extractVarName (RO _ _ _ _ comment) = parseComment comment
extractVarName (RM _ _ _ _ comment) = parseComment comment

parseComment :: String -> String
parseComment comment = 
    let parts = words comment
    in if length parts > 0 
       then let prefix = take 5 (head parts)
            in if prefix == "read:" || prefix == "write"
               then if ':' `elem` (head parts)
                    then drop ((length (takeWhile (/= ':') (head parts))) + 1) (head parts)
                    else ""
               else ""
       else ""
